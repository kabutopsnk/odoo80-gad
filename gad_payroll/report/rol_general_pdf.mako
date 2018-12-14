<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <style type="text/css">
    table { page-break-inside:auto }
    tr    { page-break-inside:avoid; page-break-after:auto }
    thead { display:table-header-group }
    tfoot { display:table-footer-group }
    </style>
</head>
<body style="overflow:scroll;">	
    %for payroll in objects:
    <table  cellspacing=0 style="font-size:8px;overflow:scroll;" width="100%" border="1" rules="rows">

	%for linea in generate_dict(payroll):
	<tr>
	  <%
	     cabecera=0
	     total=0
	     contador=0
	     departamento=0
	  %>
	  %if linea[0]=='TOTAL':
	  <%
	     total=1
	  %>
	  %endif
	  %if linea[0]=='DEPARTAMENTO':
	  <%
	     departamento=1
	  %>
	  %endif
	  %if linea[0]=='CEDULA':
	  <%
	     cabecera=1
	  %>
	  %endif
	  %for celda in linea:
	    <%
	      contador+=1
	    %>
	    %if total==1:

	      %if contador==1:
	        <th style="text-weight:bold;text-align:right;" width="5%">${celda}</th>
	      %elif contador==2:
	        <th style="text-weight:bold;text-align:right;" width="20%">${celda}</th>
	      %elif contador==3:
	        <th style="text-weight:bold;text-align:right;" width="5%">${celda}</th>
	      %else:
	        <th style="text-weight:normal;text-align:right;">${celda}</th>
	      %endif

	    %elif cabecera==1:

	      %if contador==1:
	        <th style="text-weight:bold;text-align:center;" width="5%">${celda}</th>
	      %elif contador==2:
	        <th style="text-weight:bold;text-align:center;" width="20%">${celda}</th>
	      %elif contador==3:
	        <th style="text-weight:bold;text-align:center;" width="5%">${celda}</th>
	      %else:
	        <th style="text-weight:bold;text-align:center;">${celda}</th>
	      %endif

	    %elif departamento==1:

	      %if contador==2:
	        <th style="text-weight:bold;text-align:left;" width="30%" colspan="3">${celda}</th>
	      %elif contador>3:
	        <th style="text-weight:normal;text-align:left;">${celda}</th>
	      %endif

	    %else:
	  
	      %if contador==1:
	        <th style="text-weight:normal;text-align:left;" width="5%">${celda}</th>
	      %elif contador==2:
	        <th style="text-weight:bold;text-align:left;" width="20%">${celda}</th>
	      %elif contador==3:
	        <th style="text-weight:normal;text-align:right;" width="5%">${celda}</th>
	      %else:
	        <th style="text-weight:normal;text-align:right;">${celda}</th>
	      %endif

	    %endif

	  %endfor
    	</tr>
	%endfor
    </table>
    %endfor

</body>
</html>
