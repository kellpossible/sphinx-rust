__all__ = ["rustdomain"]

from .rustdomain import RustDomain

def setup(app):
    app.add_domain(RustDomain)