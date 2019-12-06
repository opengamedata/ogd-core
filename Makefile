.PHONY: deploy

deploy:
	rsync -vrc * swansonl@fieldday-web.ad.education.wisc.edu:/var/www/opengamedata --exclude-from rsync-exclude
