from typing import List
from app import models, schemas, repository as repo


async def get_categories(
    current_user: models.User,
) -> List[models.TransactionCategory]:
    return await repo.get_all(models.TransactionCategory)


async def get_category(
    current_user: models.User, category_id: int
) -> models.TransactionCategory:
    category = await repo.get(models.TransactionCategory, category_id)

    if category and (category.user_id is None or category.user_id == current_user.id):
        return category

    return None


# async def create_category(user: models.User, category: schemas.TransactionCategory) -> models.TransactionCategory:

#     db_category = models.TransactionCategory(user=user, **category.dict())
#     await repo.save(db_category)
#     return db_category


# async def update_category(
#     current_user: models.User, category_id, category: schemas.TransactionCategoryData
# ) -> models.TransactionCategory:

#     db_category = await repo.get(models.TransactionCategory, category_id)
#     if db_category.user_id == current_user.id:
#         await repo.update(models.TransactionCategory, db_category.id, **category.dict())
#         return db_category

#     return None


# async def delete_category(current_user: models.User, category_id: int) -> bool:

#     category = await repo.get(models.TransactionCategory, category_id)
#     if category and category.user_id == current_user.id:
#         await repo.delete(category)
#         return True

#     return None