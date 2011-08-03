<head>
	<div id="fb-root"></div>
	<script src="http://connect.facebook.net/en_US/all.js"></script>
	<script>
	  FB.init({
	    appId  : {{ appId }}
	    status : true, // check login status
	    oauth  : true // enable OAuth 2.0
	  });
	</script>
	<link rel="stylesheet" href="/static/fbapp.css" type="text/css"/>
</head>
<body class="fbbody" dir="rtl" style="text-align: right">
<h2>צרף את סמל המחאה לתמונת הפרופיל שלך</h2>
<p>
	בחר אחד מהסמלים המצורפים להלן, והדבק אותם על תמונת הפרופיל שלך. 
	<br/>
	<b>לבחירה, לחץ על אחד הסמלים</b>
</p>
<p>
	<h2>ב' זה בית</h2>
	<a href="/render/?b=1">
		<img src="/static/bet_badge.png" class="badge_select"/>
	</a>
</p>
<p>
	<h2>העם דורש צדק חברתי</h2>
	<a href="/render/?b=2">
		<img src="/static/just_badge.png" class="badge_select"/>
	</a>
</p>
</body>