<!DOCTYPE html>
<html >
<!--From https://codepen.io/frytyler/pen/EGdtg-->
<head>
  <meta charset="UTF-8">
  <title>NL TO SPARQL</title>
  <link href='https://fonts.googleapis.com/css?family=Pacifico' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Arimo' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Hind:300' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Open+Sans+Condensed:300' rel='stylesheet' type='text/css'>
<link rel="stylesheet" href="./style.css">

</head>

<body>
 <div class="login">
	<h1>Predict SPARQL</h1>

     <!-- Main Input For Receiving Query to our ML -->
     
		<input type="text" id="queees" placeholder="Write Query here.."/>
    <input type="button"  class="btn btn-primary btn-block btn-large" value="Predict" onclick="loadDoc()"/>
    
   <br>
   <br>
   <p id="answer" style="color: white;"> You will get answer here</p>
 </div>

<script>
 
 function loadDoc() {
   
  var quees=document.getElementById('queees').value 
  console.log(quees)  
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    console.log('Harsh',this.status )
    if (this.readyState==4 && this.status == 200) {
      var data = JSON.parse(this.responseText);
      document.getElementById('answer').innerText=data.ans
      console.log(data.ans.results.bindings)
    }
  };
  xhttp.open("GET", `http://20.62.194.80:5000/getsparql/?ques=${quees}`, true);
  xhttp.send();
 }
</script>


</body>
</html>
