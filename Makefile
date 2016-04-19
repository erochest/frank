
HEROKU_APP=frankensystem

serve:
	gunicorn frank.wsgi:app --log-level debug --reload \
		--env DATABASE_URL=$(DATABASE_URL)

freeze:
	pip freeze > requirements.txt

deploy:
	BRANCH=`git branch | grep '*' | cut -f 2 -d ' '` && git checkout master && git merge $$BRANCH && git branch --delete $$BRANCH
	git push
	heroku run --app $(HEROKU_APP) -- python -m frank.wsgi db migrate
	heroku restart --app $(HEROKU_APP)

.PHONY: serve freeze deploy
