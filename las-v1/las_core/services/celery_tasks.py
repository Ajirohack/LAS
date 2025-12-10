"""
Celery Tasks for LAS - Asynchronous task processing.
"""

from .celery_app import app
from typing import Dict, Any
import time
from datetime import datetime, timedelta

@app.task(bind=True, name='services.celery_tasks.process_query')
def process_query(self, query_text: str, provider: str, model: str, **kwargs):
    """
    Process a query asynchronously.
    
    Args:
        query_text: User query
        provider: LLM provider
        model: Model name
    """
    try:
        from services.llm_service import get_llm_service
        from services.interaction_service import get_interaction_service
        
        # Update task state
        self.update_state(state='PROCESSING', meta={'query': query_text})
        
        # Get services
        interaction = get_interaction_service()
        
        # Process query
        result = interaction.query_sync(query_text, provider=provider, model=model)
        
        return {
            "status": "success",
            "result": result,
            "completed_at": datetime.now().isoformat()
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@app.task(bind=True, name='services.celery_tasks.scrape_website')
def scrape_website(self, url: str, extract_type: str = "full"):
    """
    Scrape a website asynchronously.
    
    Args:
        url: URL to scrape
        extract_type: Type of extraction (full, text, links)
    """
    try:
        from sources.browser import Browser, create_driver
        
        self.update_state(state='SCRAPING', meta={'url': url})
        
        # Create browser instance
        driver = create_driver(headless=True)
        browser = Browser(driver)
        
        # Navigate and scrape
        driver.get(url)
        time.sleep(2)  # Wait for page load
        
        content = {
            "url": url,
            "title": driver.title,
            "text": browser.get_text() if extract_type in ["full", "text"] else None,
            "html": driver.page_source if extract_type == "full" else None,
            "scraped_at": datetime.now().isoformat()
        }
        
        driver.quit()
        
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@app.task(name='services.celery_tasks.analyze_image')
def analyze_image(image_path: str, prompt: str = "Describe this image"):
    """Analyze image using vision service."""
    try:
        from services.vision_service import get_vision_service
        
        vision = get_vision_service()
        analysis = vision.analyze_image(image_path, prompt=prompt)
        
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.task(name='services.celery_tasks.check_worker_health')
def check_worker_health():
    """Periodic task to check worker health."""
    from services.worker_pool import get_worker_pool
    
    pool = get_worker_pool()
    offline_workers = []
    
    for worker in pool.list_workers():
        if not pool.health_check(worker.id):
            offline_workers.append(worker.id)
    
    if offline_workers:
        print(f"⚠️  Offline workers detected: {offline_workers}")
    
    return {
        "stats": pool.get_stats(),
        "offline_workers": offline_workers
    }

@app.task(name='services.celery_tasks.cleanup_old_tasks')
def cleanup_old_tasks(days_old: int = 7):
    """Clean up old completed tasks."""
    from services.task_queue import get_task_queue
    
    queue = get_task_queue()
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    removed = 0
    for task_id, task in list(queue.tasks.items()):
        if task.get("completed_at"):
            completed = datetime.fromisoformat(task["completed_at"])
            if completed < cutoff_date:
                del queue.tasks[task_id]
                removed += 1
    
    return {
        "removed_count": removed,
        "cutoff_date": cutoff_date.isoformat()
    }
