from app.extensions import db
from sqlalchemy import Column, Integer, String, UniqueConstraint, CheckConstraint


class Word(db.Model):
	__tablename__ = 'words'


	ID = 'id'
	LANG = 'lang'
	CONTENT = 'content'
	TABOOS = 'taboos'


	id = Column(Integer, primary_key=True, index=True)
	lang = Column(String(10), nullable=False)
	content = Column(String(255), nullable=False)
	taboos = Column(db.JSON, nullable=False, default=list)


	__table_args__ = (
		UniqueConstraint('lang', 'content', name='unique_lang_content'),
		CheckConstraint("length(trim(content)) > 0", name='content_not_empty'),
		CheckConstraint("length(trim(lang)) > 0", name='lang_not_empty'),
	)


	def to_dict(self):
		return {
			self.ID: self.id,
			self.LANG: self.lang,
			self.CONTENT: self.content,
			self.TABOOS: self.taboos,
		}


	def __repr__(self):
		return f"<Word(id={self.id}, lang={self.lang}, content={self.content})>"
