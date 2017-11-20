from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, query_service
from .. import media_aggregator, query_extractor, summarizer 
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
