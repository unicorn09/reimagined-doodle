<!DOCTYPE html>
<html >
<!--From https://codepen.io/frytyler/pen/EGdtg-->
<head>
  <meta charset="UTF-8">
  <title>Knowledge Based System</title>
  <link href='https://fonts.googleapis.com/css?family=Pacifico' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Arimo' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Hind:300' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Open+Sans+Condensed:300' rel='stylesheet' type='text/css'>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
<link rel="stylesheet" href="./style.css">
<style>
html{
  overflow-y:scroll;
}
</style>
</head>

<body>
 <div class="login">
	<h1>Knowledge Based System</h1>

     <!-- Main Input For Receiving Query to our ML -->
     
		<input type="text" id="queees" placeholder="Write Query here.."/>
    <input type="button"  class="btn btn-primary btn-block btn-large" value="Predict" onclick="loadDoc()"/>
    
   <br>
   <br>
   <div id="answer" style="color: white; font-size: 10px;"> You will get answer here</div>

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
      var temp={};
      
      for (var i in data.ans.results.bindings){
        for(var j in data.ans.results.bindings[i]){
          for(var k in data.ans.results.bindings[i][j] ){
              if(k=='value'){
                if(!(JSON.stringify(j) in temp))
                temp[JSON.stringify(j)]=[];
               
                temp[JSON.stringify(j)].push(JSON.stringify(data.ans.results.bindings[i][j][k]));

              }
              
            }
          
        }

      }
      var line1,line2;
      result={}
      line1="<table class=\"table  table-bordered\"  style=\"color:white\"><thead>";
      line2="<tbody>";
      for(var i in temp){
        line1+="<th>"+i+"</th>";
        for(var j=0;j<temp[i].length;j++)
        {
          if(!(j in result))
          result[j]=[]
          result[j].push("<td>"+temp[i][j]+"</td>")
        }

      }
      line1+="</thead>";
      for(var i in result){
        line2+="<tr>"+result[i]+"</tr>";
      }
      line2+="</tbody></table>";
      document.getElementById('answer').innerHTML=line1+line2;
  
      console.log(data.ans.results.bindings)
    }
  };
  xhttp.open("GET", `http://20.51.247.56:5000/getsparql/?ques=${quees}`, true);
  xhttp.send();
 }
</script>


</body>
</html>
