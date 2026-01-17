from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import get_db
from .schemas import TopProduct, ChannelActivity, MessageSearch, VisualContentStats

app = FastAPI(
    title="Ethiopian Medical Data Warehouse API",
    description="API for accessing medical business insights from Telegram data.",
    version="1.0.0"
)

@app.get("/api/reports/top-products", response_model=List[TopProduct])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the most frequently mentioned keywords (simple word count) from messages.
    Focuses on words > 3 characters to avoid potential noise.
    """
    try:
        query = text("""
            SELECT lower(word) as keyword, count(*) as frequency
            FROM (
                SELECT unnest(string_to_array(message_text, ' ')) as word 
                FROM raw.telegram_messages
                WHERE message_text IS NOT NULL
            ) t
            WHERE length(word) > 3
            GROUP BY lower(word)
            ORDER BY frequency DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).fetchall()
        return [{"keyword": row[0], "frequency": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns specific activity stats for a given channel.
    """
    query = text("""
        SELECT 
            channel_name, 
            COUNT(*) as post_count, 
            COALESCE(AVG(views), 0) as avg_views 
        FROM raw.telegram_messages 
        WHERE channel_name = :channel_name
        GROUP BY channel_name
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    return [{"channel_name": row[0], "post_count": row[1], "avg_views": row[2]} for row in result]

@app.get("/api/search/messages", response_model=List[MessageSearch])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Search for messages containing a keyword.
    """
    sql_query = text("""
        SELECT id, message_date, channel_name, message_text, views 
        FROM raw.telegram_messages 
        WHERE message_text ILIKE :query 
        LIMIT :limit
    """)
    result = db.execute(sql_query, {"query": f"%{query}%", "limit": limit}).fetchall()
    
    return [
        {
            "id": row[0], 
            "date": row[1], 
            "channel": row[2], 
            "text": row[3], 
            "views": row[4]
        } for row in result
    ]

@app.get("/api/reports/visual-content", response_model=List[VisualContentStats])
def get_visual_content_stats(db: Session = Depends(get_db)):
    """
    Returns statistics on image content (Promotional vs Product vs Lifestyle)
    and their average views.
    """
    query = text("""
        SELECT 
            image_category as category,
            COUNT(*) as count,
            COALESCE(ROUND(AVG(m.views)), 0) as avg_views
        FROM raw.yolo_detections d
        JOIN raw.telegram_messages m ON d.message_id::TEXT = m.message_id::TEXT 
            AND d.channel_name = m.channel_name
        GROUP BY image_category
        ORDER BY avg_views DESC
    """)
    result = db.execute(query).fetchall()
    
    return [
        {"category": row[0], "count": row[1], "avg_views": row[2]} 
        for row in result
    ]
