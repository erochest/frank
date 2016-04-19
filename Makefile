
serve:
	gunicorn frank.wsgi:app --log-level debug --reload \
		--env DATABASE_URL=$(DATABASE_URL)

freeze:
	pip freeze > requirements.txt

.PHONY: serve freeze

