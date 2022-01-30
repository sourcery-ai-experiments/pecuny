from .. import repository as repo, models, schemas


def get_accounts(current_user: models.User) -> List[models.Account]:
    accounts = repo.filter("Account", "user_id", current_user.id).all()

    return accounts


def get_account(current_user: models.User, account_id: int) -> models.Account:

    account = repo.get("Account", account_id)
    if account and account.user_id == current_user.id:
        return account

    return None


def create_account(user: models.User, account: schemas.Account) -> models.Account:

    db_account = models.Account(
        user=user,
        **account.dict(),
    )

    repo.save(db_account)

    return db_account


def update(current_user: models.User, account: models.Account) -> models.Account:

    if account._user_id == current_user.id:
        repo.save(account)

        return account


def delete(current_user: models.User, account_id: int) -> bool:

    account = repo.get("Account", account_id)
    if account and account.user_id == current_user.id:

        repo.delete(account)
        return True

    return None
