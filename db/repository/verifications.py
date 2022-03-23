from py import code
from sqlalchemy.orm import Session

from core.hashing import Hasher
from db.models.verifications import CodeVerification
from schemas.token import TokenData as VerificationSchema


def save_verification_code(
    verification: VerificationSchema, db: Session
) -> CodeVerification:
    verif = CodeVerification(
        user_email=verification.email,
        hashed_code=Hasher.get_password_hash(verification.code),  # save hash code
    )
    db.add(verif)
    db.commit()
    db.refresh(verif)

    return verif


def get_code_by_email(email: str, db: Session) -> CodeVerification:
    return (
        db.query(CodeVerification).filter(CodeVerification.user_email == email).first()
    )


def verification_check(data: VerificationSchema, db: Session):
    if not data.code or not data.email:
        return 0

    # The given code her is in plain text
    hash_code = Hasher.get_password_hash(data.code)

    existing_data = db.query(CodeVerification).filter(
        CodeVerification.hashed_code == hash_code
    )
    if not existing_data:
        return 0
    return 1


def delete_verification_code(hash_code: str, db: Session):
    """
    This method allow to delete a verification code using a given hash

    Args:
        hash_code (str): given hash code
        db (Session): database session
    """
    existing_code = db.query(CodeVerification).filter(
        CodeVerification.hashed_code == hash_code
    )
    if not existing_code:
        return 0
    existing_code.delete(synchronize_session=False)
    return 1
