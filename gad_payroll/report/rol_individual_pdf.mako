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
<body>
    %for payslip in objects:
    <table  cellspacing=0 width="100%">
    <tr><td width="45%">
<!-- COLUMNA 1 -->
    <table  cellspacing=0 width="100%">
    	<tr>
    	<td width="15%"><center><b>${helper.embed_logo_by_name('rol_logo',width=50,height=50)|n}</b></center></td>
    	<td width="70%"><center><b>${company.name}</b><br>ROL DE PAGOS</center></td>
    	<td width="15%"></td>
    	</tr>
    </table>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="100%">
    	<tr>
    	<th width="15%"><b>Cedula:</b></th>
    	<td width="35%">${payslip.employee_id.name}</td>
    	<th width="15%"><b>Servidor:</b></th>
    	<td width="35%">${payslip.employee_id.name_related}</td>
    	</tr><tr>
    	<th width="15%"><b>Departamento:</b></th>
    	<td width="35%">${payslip.department_id.name}</td>
    	<th width="15%"><b>Cargo:</b></th>
    	<td width="35%">${payslip.job_id.name}</td>
    	</tr><tr>
    	<th width="15%"><b>Tipo:</b></th>
	%if payslip.payroll_type=='monthly':
    	<td width="35%">Mensual</td>
	%elif payslip.payroll_type=='bi-weekly':
    	<td width="35%">Quincenal</td>
	%elif payslip.payroll_type=='decimo13':
    	<td width="35%">Décimo 13</td>
	%elif payslip.payroll_type=='decimo14':
    	<td width="35%">Décimo 14</td>
	%else:
    	<td width="35%">Otro</td>
	%endif
    	<th width="15%"><b>Período:</b></th>
    	<td width="35%">${payslip.date_from} - ${payslip.date_to}</td>
    	</tr>
    </table>
    <br/>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="50%" border="1">
    	<tr>
    	<th width="70%"><b>Ausencia</b></th>
    	<th width="30%"><b>Cantidad</b></th>
    	</tr>
	%for worked_line in payslip.worked_days_line_ids:
	<tr>
    	<td width="70%">${worked_line.name}</td>
    	<td width="30%">${worked_line.number_of_days}</td>
    	</tr>
	%endfor
    </table>
    <br/>
	<%
	     ingresos=0
	     egresos=0
	%>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="100%" border="1">
    	<tr>
    	<th width="50%"><center><b>INGRESOS</b></center></th>
    	<th width="50%"><center><b>EGRESOS</b></center></th>
    	</tr>
    	<tr>
    	<td width="50%" style="vertical-align:top;">
	%for line in payslip.line_ids:
		<table  cellspacing=0 width="100%" style="font-size:10px;">
		%if (line.category_id.code == 'APT') or (line.category_id.code == 'BASIC') or (line.category_id.code == 'ING'):
			<tr style="vertical-align:top;">
			<%
			ingresos+=line.total
			%>
				<td width="75%" style="text-align:left;">${line.name}</td>
				<td width="25%" style="text-align:right;">${line.total}</td>
			</tr>
		%endif
		</table>
	%endfor
	</th>
    	<td width="50%" style="vertical-align:top;">
	%for line in payslip.line_ids:
		<table  cellspacing=0 width="100%" style="font-size:10px;">
		%if (line.category_id.code == 'EGR'):
			<%
			egresos+=line.total
			%>
			<tr style="vertical-align:top;">
				<td width="75%" style="text-align:left;">${line.name}</td>
				<td width="25%" style="text-align:right;">${line.total}</td>
			</tr>
		%endif
		</table>
	%endfor
	</th>
    	</tr><tr>
    	<th width="50%">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
			<td width="75%" style="text-align:left;"><b>TOTAL INGRESOS</b></td>
			<td width="25%" style="text-align:right;"><b>${ingresos}</b></td>
		</tr>
	    </table>
	</th>
    	<td width="50%">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
			<td width="75%" style="text-align:left;"><b>TOTAL EGRESOS</b></td>
			<td width="25%" style="text-align:right;"><b>${egresos}</b></td>
		</tr>
	    </table>
	</th>
    	</tr><tr><td colspan="2">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
	%for line in payslip.line_ids:
		%if (line.category_id.code == 'NET'):
			<td width="75%" style="text-align:left;"><b>TOTAL</b></td>
			<td width="25%" style="text-align:right;"><b>${line.total}</b></td>
		%endif
	%endfor
		</tr>
	    </table>
    	</td></tr>
    	<tr>
		<th width="100%" colspan="2">La transferencia será realizada al número de cuenta ${payslip.employee_id.bank_account_id.acc_number or '-'} del BANCO DE GUAYAQUIL</th>
    	</tr>
    	<tr>
		<th width="100%" colspan="2">${payslip.payslip_run_id.notes or ' '}</th>
    	</tr>
    	<tr>
    	<th width="50%" height="50px" style="vertical-align:bottom;text-align:center;">APROBADO POR:</th>
    	<th width="50%" height="50px" style="vertical-align:bottom;text-align:center;">EMPLEADO:</th>
    	</tr>

    </table>
<!-- FIN COLUMNA 1 -->
    </td><td width="10%"/><td width="45%">
<!-- COLUMNA 2 -->
    <table  cellspacing=0 width="100%">
    	<tr>
    	<td width="15%"><center><b>${helper.embed_logo_by_name('rol_logo',width=50,height=50)|n}</b></center></td>
    	<td width="70%"><center><b>${company.name}</b><br>ROL DE PAGOS</center></td>
    	<td width="15%"></td>
    	</tr>
    </table>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="100%">
    	<tr>
    	<th width="15%"><b>Cedula:</b></th>
    	<td width="35%">${payslip.employee_id.name}</td>
    	<th width="15%"><b>Servidor:</b></th>
    	<td width="35%">${payslip.employee_id.name_related}</td>
    	</tr><tr>
    	<th width="15%"><b>Departamento:</b></th>
    	<td width="35%">${payslip.department_id.name}</td>
    	<th width="15%"><b>Cargo:</b></th>
    	<td width="35%">${payslip.job_id.name}</td>
    	</tr><tr>
    	<th width="15%"><b>Tipo:</b></th>
	%if payslip.payroll_type=='monthly':
    	<td width="35%">Mensual</td>
	%elif payslip.payroll_type=='bi-weekly':
    	<td width="35%">Quincenal</td>
	%elif payslip.payroll_type=='decimo13':
    	<td width="35%">Décimo 13</td>
	%elif payslip.payroll_type=='decimo14':
    	<td width="35%">Décimo 14</td>
	%else:
    	<td width="35%">Otro</td>
	%endif
    	<th width="15%"><b>Período:</b></th>
    	<td width="35%">${payslip.date_from} - ${payslip.date_to}</td>
    	</tr>
    </table>
    <br/>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="50%" border="1">
    	<tr>
    	<th width="70%"><b>Ausencia</b></th>
    	<th width="30%"><b>Cantidad</b></th>
    	</tr>
	%for worked_line in payslip.worked_days_line_ids:
	<tr>
    	<td width="70%">${worked_line.name}</td>
    	<td width="30%">${worked_line.number_of_days}</td>
    	</tr>
	%endfor
    </table>
    <br/>
	<%
	     ingresos=0
	     egresos=0
	%>
    <table  cellspacing=0 style="text-align:left;font-size:10px" width="100%" border="1">
    	<tr>
    	<th width="50%"><center><b>INGRESOS</b></center></th>
    	<th width="50%"><center><b>EGRESOS</b></center></th>
    	</tr>
    	<tr>
    	<td width="50%" style="vertical-align:top;">
	%for line in payslip.line_ids:
		<table  cellspacing=0 width="100%" style="font-size:10px;">
		%if (line.category_id.code == 'APT') or (line.category_id.code == 'BASIC') or (line.category_id.code == 'ING'):
			<tr style="vertical-align:top;">
			<%
			ingresos+=line.total
			%>
				<td width="75%" style="text-align:left;">${line.name}</td>
				<td width="25%" style="text-align:right;">${line.total}</td>
			</tr>
		%endif
		</table>
	%endfor
	</th>
    	<td width="50%" style="vertical-align:top;">
	%for line in payslip.line_ids:
		<table  cellspacing=0 width="100%" style="font-size:10px;">
		%if (line.category_id.code == 'EGR'):
			<tr style="vertical-align:top;">
			<%
			egresos+=line.total
			%>
				<td width="75%" style="text-align:left;">${line.name}</td>
				<td width="25%" style="text-align:right;">${line.total}</td>
			</tr>
		%endif
		</table>
	%endfor
	</th>
    	</tr><tr>
    	<th width="50%">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
			<td width="75%" style="text-align:left;"><b>TOTAL INGRESOS</b></td>
			<td width="25%" style="text-align:right;"><b>${ingresos}</b></td>
		</tr>
	    </table>
	</th>
    	<td width="50%">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
			<td width="75%" style="text-align:left;"><b>TOTAL EGRESOS</b></td>
			<td width="25%" style="text-align:right;"><b>${egresos}</b></td>
		</tr>
	    </table>
	</th>
    	</tr><tr><td colspan="2">
	    <table  cellspacing=0 width="100%" style="font-size:10px">
		<tr>
	%for line in payslip.line_ids:
		%if (line.category_id.code == 'NET'):
			<td width="75%" style="text-align:left;"><b>TOTAL</b></td>
			<td width="25%" style="text-align:right;"><b>${line.total}</b></td>
		%endif
	%endfor
		</tr>
	    </table>
    	</td></tr>
    	<tr>
		<th width="100%" colspan="2">La transferencia será realizada al número de cuenta ${payslip.employee_id.bank_account_id.acc_number or '-'} del BANCO DE GUAYAQUIL</th>
    	</tr>
    	<tr>
		<th width="100%" colspan="2">${payslip.payslip_run_id.notes or ' '}</th>
    	</tr>
    	<tr>
    	<th width="50%" height="50px" style="vertical-align:bottom;text-align:center;">APROBADO POR:</th>
    	<th width="50%" height="50px" style="vertical-align:bottom;text-align:center;">EMPLEADO:</th>
    	</tr>

    </table>
<!-- FIN COLUMNA 2 -->
    </td></tr>
    </table>
  <p style="page-break-after:always"></p>
  %endfor
</body>
</html>
