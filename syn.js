var timeOutMS = 5000; //ms
var ajaxList = new Array();
function ajxCmd(url, container, repeat, data)
{
	// Set up our object
	var newAjax = new Object();
	var theTimer = new Date();
	newAjax.url = url;
	newAjax.container = container;
	newAjax.repeat = repeat;
	newAjax.ajaxReq = null;
	
	// Create and send the request
	if(window.XMLHttpRequest) {
        newAjax.ajaxReq = new XMLHttpRequest();
        newAjax.ajaxReq.open((data==null)?"GET":"POST", newAjax.url, true);
        newAjax.ajaxReq.send(data);
    // If we're using IE6 style (maybe 5.5 compatible too)
    } else if(window.ActiveXObject) {
        newAjax.ajaxReq = new ActiveXObject("Microsoft.XMLHTTP");
        if(newAjax.ajaxReq) {
            newAjax.ajaxReq.open((data==null)?"GET":"POST", newAjax.url, true);
            newAjax.ajaxReq.send(data);
        }
    }
    
    newAjax.lastCalled = theTimer.getTime();
    
    // Store in our array
    ajaxList.push(newAjax);
}

function pollAJAX() {
	var curAjax = new Object();
	var theTimer = new Date();
	var elapsed;
	
	// Read off the ajaxList objects one by one
	for(i = ajaxList.length; i > 0; i--)
	{
		curAjax = ajaxList.shift();
		if(!curAjax)
			continue;
		elapsed = theTimer.getTime() - curAjax.lastCalled;
				
		// If we suceeded
		if(curAjax.ajaxReq.readyState == 4 && curAjax.ajaxReq.status == 200) {
			// If it has a container, write the result
			if(typeof(curAjax.container) == 'function'){
				curAjax.container(curAjax.ajaxReq.responseXML.documentElement);
			} else if(typeof(curAjax.container) == 'string') {
				document.getElementById(curAjax.container).innerHTML = curAjax.ajaxReq.responseText;
			} // (otherwise do nothing for null values)
			
	    	curAjax.ajaxReq.abort();
	    	curAjax.ajaxReq = null;

			// If it's a repeatable request, then do so
			if(curAjax.repeat)
				ajxCmd(curAjax.url, curAjax.container, curAjax.repeat);
			continue;
		}
		
		// If we've waited over 1 second, then we timed out
		if(elapsed > timeOutMS) {
			// Invoke the user function with null input
			if(typeof(curAjax.container) == 'function'){
				curAjax.container(null);
			} 
			else {
			//	alert("Command failed.\nConnection to the unit was lost.");
			}

	    	curAjax.ajaxReq.abort();
	    	curAjax.ajaxReq = null;
			
			// If it's a repeatable request, then do so
			if(curAjax.repeat)
				ajxCmd(curAjax.url, curAjax.container, curAjax.repeat);
			continue;
		}
		
		// Otherwise, just keep waiting
		ajaxList.push(curAjax);
	}
	
	// Call ourselves again in 600ms synaccess
	// setTimeout("pollAJAX()",600);
	
}// End pollAjax
			
function getXMLValue(xmlData, field) {
	try {
		if(xmlData.getElementsByTagName(field)[0].firstChild.nodeValue)
			return xmlData.getElementsByTagName(field)[0].firstChild.nodeValue;
		else
			return null;
	} catch(err) { return null; }
}

// start infinite loop for ajax loop at 600ms
setInterval(pollAJAX, 600);
var attempts = 0;
var logout_ajax = function (status) {
	var rq = new XMLHttpRequest();
	var reqListener = function() {
    if (rq.status !== 200) {
      // try again
      if (attempts < 10) {
        logout_ajax(status);
      }
      attempts++;

    } else {
        document.location.href="/";     
    }
  }
	rq.addEventListener("load", reqListener);
	rq.open("GET", status === "timeout" ? "/cmd.cgi?clrR=10" : "/cmd.cgi?clrR=11");
	rq.send();
}

var t;
    // DOM Events
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;

    function logout() {
      logout_ajax("timeout");	
    }

    function resetTimer() {
        clearTimeout(t);
        t = setTimeout(logout, 300000)
        // 1000 milisec = 1 sec
    }

window.onload = function() {
var btn = document.getElementById("lgout");
if (btn) {
  btn.onclick = function(){
    logout_ajax("clicked");
  }
}
resetTimer();
}
var newwindow;
function acctOp(op, n)  
 { 
	if ((op == '1') || (op=='2')){
		var logfader = document.getElementById('login_fader');
		var logbox;
		if (op == '1') logbox = document.getElementById('login_box');
		else if (op == '2') logbox = document.getElementById('change_box');		
		logfader.style.display = "block";
		logbox.style.display = "block";
	}
	else  {
	  var logfader = document.getElementById('show_fader');
	  var logbox;
        if ((op == '3')) logbox = document.getElementById('show_tc');
        else logbox = document.getElementById('show_lc');
        

        logfader.style.display = "block";
        logbox.style.display = "block";
	}
 } 