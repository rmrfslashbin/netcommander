

function updateStatus(xmlData) {
	// Check if a timeout occurred
	if(!xmlData)
	{
		document.getElementById('display').style.display = 'none';
		document.getElementById('loading').style.display = 'inline';
		return;
	}

	document.getElementById('loading').style.display = 'none';
	document.getElementById('display').style.display = 'inline';

	for(i = 0; i <= 4; i++) {
		if(getXMLValue(xmlData, 'rly'+i) == '1')
			document.getElementById('rly' + i).innerHTML = '<img alt="on" src="on.gif" />';
		else
			document.getElementById('rly' + i).innerHTML = '<img alt="off" src="off.gif" />';
	}

	for(i = 0; i <= 8; i++) 
		document.getElementById('ac'+i).innerHTML = getXMLValue(xmlData, 'ac'+i);

	for(i = 11; i <= 17; i++) 
		document.getElementById('ac'+i).innerHTML = getXMLValue(xmlData, 'ac'+i);

        i = 30;
        document.getElementById('ac'+i).innerHTML = getXMLValue(xmlData, 'ac'+i);

	for(i = 0; i <= 3; i++) 
		document.getElementById('tp'+i).innerHTML = getXMLValue(xmlData, 'tp'+i);
	
	for(i = 1; i <= 2; i++) 
		document.getElementById('tcp'+i).innerHTML = getXMLValue(xmlData, 'tcp'+i);

	for(i = 30; i <= 34; i++) 
		document.getElementById('apa'+i).innerHTML = getXMLValue(xmlData, 'apa'+i);
		
	for(i = 50; i <= 54; i++) 
		document.getElementById('apa'+i).innerHTML = getXMLValue(xmlData, 'apa'+i);
	for(i = 70; i <= 74; i++) 
		document.getElementById('apa'+i).innerHTML = getXMLValue(xmlData, 'apa'+i);

	document.getElementById('err1').innerHTML = getXMLValue(xmlData, 'err1');
}
setTimeout("ajxCmd('status.xml', updateStatus, true)",500);
<!--

//-->