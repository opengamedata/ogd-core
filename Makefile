.PHONY: deploy

deploy:
	rsync -vrc * fieldday-web.ad.education.wisc.edu:/var/www/opengamedata --exclude-from rsync-exclude

deploy-extractors:
	rsync -vrc ./games/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games --exclude-from rsync-exclude

deploy-aqualab:
	rsync -vrc ./games/AQUALAB/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/AQUALAB --exclude-from rsync-exclude
deploy-lakeland:
	rsync -vrc ./games/LAKELAND/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/LAKELAND --exclude-from rsync-exclude
deploy-shadowspect:
	rsync -vrc ./games/SHADOWSPECT/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/SHADOWSPECT --exclude-from rsync-exclude