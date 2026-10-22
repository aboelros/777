"""
Legacy Models Proxy.
All models have been modularized into app.domains.*.models.
This file proxies the imports to preserve backward compatibility for tests and legacy scripts.
"""

from app.domains.auth.models import *
from app.domains.projects.models import *
from app.domains.integrations.models import *
from app.domains.orders.models import *
from app.domains.messages.models import *
from app.domains.ai.models import *
from app.domains.analytics.models import *
from app.domains.products.models import *
from app.domains.social.models import *
from app.domains.customers.models import *
from app.domains.billing.models import *
from app.domains.crm.models import *
from app.domains.apps.models import *
from app.domains.webhooks.models import *
