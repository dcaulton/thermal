import uuid

from flask import current_app, url_for

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (get_documents_from_criteria,
                           get_document,
                           item_exists,
                           save_document)
