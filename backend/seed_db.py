import pandas as pd
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Recruitment, Portfolio, CoverLetter
import os

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Seed Users
        if os.path.exists("users_sample.csv"):
            users_df = pd.read_csv("users_sample.csv")
            for _, row in users_df.iterrows():
                user = db.query(User).filter(User.email == row['email']).first()
                if not user:
                    user = User(
                        id=row['id'],
                        email=row['email'],
                        name=row['name'],
                        profile_image=row.get('profile_image')
                    )
                    db.add(user)
            db.commit()
            print("Users seeded.")

        # 2. Seed Recruitments
        if os.path.exists("recruitments_sample.csv"):
            recruits_df = pd.read_csv("recruitments_sample.csv")
            for _, row in recruits_df.iterrows():
                recruit = db.query(Recruitment).filter(Recruitment.id == row['id']).first()
                if not recruit:
                    # Convert date strings if necessary, but sqlalchemy Date expects datetime.date
                    # For simplicity, assuming strings are in correct format or letting pandas handle it
                    recruit = Recruitment(
                        id=row['id'],
                        title=row['title'],
                        company=row['company'],
                        content=row.get('content'),
                        category=row.get('category')
                    )
                    # Handle tags if it's a JSON/List
                    if 'tags' in row and pd.notna(row['tags']):
                        import json
                        try:
                            recruit.tags = json.loads(row['tags'].replace("'", '"'))
                        except:
                            recruit.tags = [row['tags']]
                    db.add(recruit)
            db.commit()
            print("Recruitments seeded.")

        # 3. Seed Portfolios
        if os.path.exists("portfolios_sample.csv"):
            portfolios_df = pd.read_csv("portfolios_sample.csv")
            for _, row in portfolios_df.iterrows():
                portfolio = db.query(Portfolio).filter(Portfolio.id == row['id']).first()
                if not portfolio:
                    portfolio = Portfolio(
                        id=row['id'],
                        title=row['title'],
                        type=row['type'],
                        source_url=row.get('source_url'),
                        content=row.get('content'),
                        user_id=row['user_id']
                    )
                    db.add(portfolio)
            db.commit()
            print("Portfolios seeded.")

        # 4. Seed Cover Letters
        if os.path.exists("cover_letters_sample.csv"):
            letters_df = pd.read_csv("cover_letters_sample.csv")
            for _, row in letters_df.iterrows():
                letter = db.query(CoverLetter).filter(CoverLetter.id == row['id']).first()
                if not letter:
                    letter = CoverLetter(
                        id=row['id'],
                        title=row.get('title'),
                        content=row.get('content'),
                        user_id=row['user_id'],
                        recruitment_id=row['recruitment_id']
                    )
                    db.add(letter)
            db.commit()
            print("Cover Letters seeded.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
