
from pythonic.models import User, Availability

def get_plumbing_users_from_database(page, per_page):
    plumbing_pagination = User.query.filter_by(service_type='plumbing').paginate(page=page, per_page=per_page, error_out=False)
    total_users = plumbing_pagination.total
    total_pages = plumbing_pagination.pages
    return plumbing_pagination.items, total_users, total_pages


def get_electrical_users_from_database(page, per_page):
    electrical_pagination = User.query.filter_by(service_type='electrical').paginate(page=page, per_page=per_page, error_out=False)
    total_users = electrical_pagination.total
    total_pages = electrical_pagination.pages
    return electrical_pagination.items, total_users, total_pages

def get_cleaning_users_from_database(page, per_page):
    cleaning_pagination = User.query.filter_by(service_type='Cleaning').paginate(page=page, per_page=per_page, error_out=False)
    total_users = cleaning_pagination.total
    total_pages = cleaning_pagination.pages
    return cleaning_pagination.items, total_users, total_pages

def get_movingFur_users_from_database(page, per_page):
    movingFur_pagination = User.query.filter_by(service_type='Moving Furniture').paginate(page=page, per_page=per_page, error_out=False)
    total_users = movingFur_pagination.total
    total_pages = movingFur_pagination.pages
    return movingFur_pagination.items, total_users, total_pages

def get_Painting_users_from_database(page, per_page):
    Painting_pagination = User.query.filter_by(service_type='Painting').paginate(page=page, per_page=per_page, error_out=False)
    total_users = Painting_pagination.total
    total_pages = Painting_pagination.pages
    return Painting_pagination.items, total_users, total_pages

def get_Carpentry_users_from_database(page, per_page):
    Carpentry_pagination = User.query.filter_by(service_type='Carpentry').paginate(page=page, per_page=per_page, error_out=False)
    total_users = Carpentry_pagination.total
    total_pages = Carpentry_pagination.pages
    return Carpentry_pagination.items, total_users, total_pages