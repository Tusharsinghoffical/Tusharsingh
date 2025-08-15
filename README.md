
git add .
git commit -m "Added all website and zip files in one commit"
git push origin main
curl -X POST "https://api.render.com/deploy/srv-d28uvhmr433s73c0p52g?key=a_sQGQYrn1c"
