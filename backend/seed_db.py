import csv
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Recruitment, Portfolio, CoverLetter

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Seed Users
        if os.path.exists("users_sample.csv"):
            with open("users_sample.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = db.query(User).filter(User.email == row['email']).first()
                    if not user:
                        user = User(
                            id=int(row['id']),
                            email=row['email'],
                            name=row['name'],
                            profile_image=row.get('profile_image') if row.get('profile_image') else None
                        )
                        db.add(user)
            db.commit()
            print("Users seeded.")

        # 2. Seed Recruitments
        if os.path.exists("recruitments_sample.csv"):
            with open("recruitments_sample.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    recruit = db.query(Recruitment).filter(Recruitment.id == int(row['id'])).first()
                    if not recruit:
                        recruit = Recruitment(
                            id=int(row['id']),
                            title=row['title'],
                            company=row['company'],
                            content=row.get('content'),
                            category=row.get('category'),
                            location=row.get('location')
                        )
                        # Handle tags if it's a JSON/List string
                        tags_str = row.get('tags')
                        if tags_str:
                            try:
                                recruit.tags = json.loads(tags_str.replace("'", '"'))
                            except:
                                recruit.tags = [tags_str]
                        
                        db.add(recruit)
            db.commit()
            print("Recruitments seeded.")

        # 3. Seed Portfolios
        if os.path.exists("portfolios_sample.csv"):
            with open("portfolios_sample.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    portfolio = db.query(Portfolio).filter(Portfolio.id == int(row['id'])).first()
                    if not portfolio:
                        portfolio = Portfolio(
                            id=int(row['id']),
                            title=row['title'],
                            type=row['type'],
                            source_url=row.get('source_url'),
                            content=row.get('content'),
                            user_id=int(row['user_id'])
                        )
                        db.add(portfolio)
            db.commit()
            print("Portfolios seeded.")

        # 4. Seed Cover Letters
        if os.path.exists("cover_letters_sample.csv"):
            with open("cover_letters_sample.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    letter = db.query(CoverLetter).filter(CoverLetter.id == int(row['id'])).first()
                    if not letter:
                        letter = CoverLetter(
                            id=int(row['id']),
                            title=row.get('title'),
                            content=row.get('content'),
                            user_id=int(row['user_id']),
                            recruitment_id=int(row['recruitment_id'])
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
