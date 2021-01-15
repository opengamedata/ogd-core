.PHONY: deploy

deploy:
	rsync -vrc * fieldday-web.ad.education.wisc.edu:/var/www/opengamedata --exclude-from rsync-exclude
