.PHONY: deploy

deploy:
	rsync -vrc * fieldday-web.ad.education.wisc.edu:/var/www/opengamedata --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart

deploy-interfaces:
	rsync -vrc ./interfaces/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/interfaces --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart
deploy-extractors:
	rsync -vrc ./games/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart

deploy-aqualab:
	rsync -vrc ./games/AQUALAB/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/AQUALAB --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart
deploy-lakeland:
	rsync -vrc ./games/LAKELAND/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/LAKELAND --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart
deploy-shadowspect:
	rsync -vrc ./games/SHADOWSPECT/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/SHADOWSPECT --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart
deploy-shipwrecks:
	rsync -vrc ./games/SHIPWRECKS/* fieldday-web.ad.education.wisc.edu:/var/www/opengamedata/games/SHIPWRECKS --exclude-from rsync-exclude
	ssh -t fieldday-web.ad.education.wisc.edu sudo /sbin/service httpd restart
