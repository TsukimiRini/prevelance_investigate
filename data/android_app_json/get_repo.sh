#!/bin/bash
int=1
while (($int<=10))
do
	a="android-java-repo-app-p${int}"
	url="https://api.github.com/search/repositories?q=topic:android+language:java&sort=stars&order=desc&per_page=100&page=${int}"
	curl -H "Accept: application/vnd.github.mercy-preview+json" $url >> $a
 	let "int++"
 done