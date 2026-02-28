import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Word


class TestWordModel:
    def test_create_word_success(self, app_context):
        word = Word(
            lang="ES",
            content="casa",
            taboos=["hogar", "vivienda", "techo"],
        )

        db.session.add(word)
        db.session.commit()

        assert word.id == 1
        data = word.to_dict()
        assert data[Word.LANG] == "ES"
        assert data[Word.CONTENT] == "casa"
        assert data[Word.TABOOS] == ["hogar", "vivienda", "techo"]


    def test_unique_lang_content_constraint(self, app_context):
        db.session.add(Word(lang="ES", content="perro", taboos=["can", "mascota"]))
        db.session.commit()

        db.session.add(Word(lang="ES", content="perro", taboos=["animal"]))
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


    def test_allows_same_content_different_lang(self, app_context):
        db.session.add(Word(lang="ES", content="table", taboos=["mueble"]))
        db.session.add(Word(lang="EN", content="table", taboos=["furniture"]))
        db.session.commit()

        words = Word.query.filter_by(content="table").all()
        assert len(words) == 2


    def test_content_not_empty_constraint(self, app_context):
        db.session.add(Word(lang="ES", content="   ", taboos=["x"]))

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
