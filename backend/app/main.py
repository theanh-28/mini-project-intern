from app import create_app
from app.core.config import settings
import logging

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


app = create_app()

if __name__ == '__main__':
    app.run(debug=settings.debug)

logger.info(f"IAM running in {'debug' if settings.debug else 'production'} mode.")