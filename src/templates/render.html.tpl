<head>
	<div id="fb-root"></div>
	<script src="http://connect.facebook.net/en_US/all.js"></script>
	<script>
	  FB.init({
	    appId  : '{{ appId }}',
	    status : true, // check login status
	    oauth  : true // enable OAuth 2.0
	  });
	  
	  function postToWall() {
	  	if (document.getElementById('doPost').checked) {
	  	 FB.ui(
		   {
		     method: 'feed',
		     name: 'גם אני תומך במהפכה',
		     link: 'http://apps.facebook.com/julyrevolution/',
		     picture: 'http://badger.servehttp.com/static/just_badge.png',
		     caption: 'הוסיפו את האפליקציה עכשיו!',
		     description: 'הוסיפו את אפליקציית התמיכה במחאת האוהלים, ושנו את תמונת הפרופיל שלכם http://apps.facebook.com/julyrevolution/'
		   },
		   function(response) {
		      top.location.href = "{{ imageFbURL }}" + "&makeprofile=1";
		   }
		 );
		 }
		 else {
		 	top.location.href = "{{ imageFbURL }}" + "&makeprofile=1";
		 }
	  }
	</script>
	<link rel="stylesheet" href="/static/fbapp.css" type="text/css"/>
</head>
<body class="fbbody" dir="rtl" style="text-align: right">
<h2>תמונת הפרופיל החדשה שלך מוכנה!</h2>
<p>
	<h3>
		כיצד להפוך את התמונה לתמונת הפרופיל שלי?
	</h3>
	<input type="checkbox" id="doPost" checked="checked"/> פרסם הודעה על הקיר שלי
	<ol>
		<li>לחץ על התמונה כדי להגיע לעמוד התמונה בפייסבוק</li>
		<li>בעמוד התמונה לחץ על  "הפוך לתמונת פרופיל"</li>
	</ol>
</p>
<p>
	<a href="#" onclick="postToWall()">
		<img src="/static/{{ imageURL }}" class="profile_img"/>
	</a>
	<br/>
	<div class="fbbluebox" style="width:250px">
		<a href="#" onclick="postToWall()">
		עבור לעמוד התמונה והפוך לתמונת הפרופיל
		</a>
	</div>
	
	<br/><br/>
	<div class="fbbluebox" style="width:150px">
		<a href="/select/">
		חזרה לבחירת סמל אחר
		</a>
	</div>
</p>
</body>