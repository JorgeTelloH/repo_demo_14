# -*- coding: utf-8 -*-
# class AccountingQueries():
import logging

from itertools import *

_logger=logging.getLogger(__name__)

def query_account_amount_balances(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """select 
		case
		when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
		else table_saldos_iniciales.id 
		end id,
		case
		when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
		else table_saldos_iniciales.name 
		end,
		case 
		when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
		else table_saldos_iniciales.code 
		end code
		,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
		credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,
		table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo 
		from
		(select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit) as debit_saldo_inicial,sum(aml.credit) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id 
		join account_account_type acact on acact.id=acac.user_type_id
		where
		acact.include_initial_balance=True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		group by acac.id
		UNION
		select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit) as debit_saldo_inicial,sum(aml.credit) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join 
		account_account_type acact on acact.id=acac.user_type_id 
		where
		acact.include_initial_balance<>True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id) as table_saldos_iniciales
		
		full outer join 
		
		(select acac.code as code,acac.name as name,acac.id as id,sum(aml.debit) as debit_movimiento_periodo,sum(aml.credit) as credit_movimiento_periodo from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_account_type acact on acact.id=acac.user_type_id
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id
		where
		abs(coalesce(table_saldos_iniciales.debit_saldo_inicial - table_saldos_iniciales.credit_saldo_inicial,0.00))>0.00 or
		table_movimientos_periodo.debit_movimiento_periodo >0.00 or
		table_movimientos_periodo.credit_movimiento_periodo >0.00
		order by code """ % (
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total

###################################################################################################################
def query_account_amount_balances_opening_balances_ids(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """
		select aml.id from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id 
		join account_account_type acact on acact.id=acac.user_type_id
		where
		acact.include_initial_balance=True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		UNION
		select aml.id from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join 
		account_account_type acact on acact.id=acac.user_type_id 
		where
		acact.include_initial_balance<>True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s"""%(
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras)

	return query_total

######################################################################################################################
def query_account_amount_balances_period_balances_ids(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):

	query_total= """
		select aml.id  from 
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id 
		join account_account_type acact on acact.id=acac.user_type_id
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s
		"""%(
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)

	return query_total
######################################################################################################################
##################################################################################################

def query_account_amount_balances_currency_native(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """select 
		case
		when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
		else table_saldos_iniciales.id 
		end id,
		case
		when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
		else table_saldos_iniciales.name 
		end,
		case 
		when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
		else table_saldos_iniciales.code 
		end code
		,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
		credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,
		table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo 
		from
		(select acac.code as code,acac.name as name,acac.id as id ,sum(case 
					   when coalesce(aml.amount_currency,0.00)<0.00 then 0.00 
					   else abs(coalesce(aml.amount_currency,0.00)) end) as debit_saldo_inicial,sum(case when coalesce(aml.amount_currency,0.00)>0.00 then 0.00 else abs(coalesce(aml.amount_currency,0.00)) end) 
					   as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id 
		join account_account_type acact on acact.id=acac.user_type_id
		where
		acact.include_initial_balance=True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		group by acac.id
		UNION
		select acac.code as code,acac.name as name,acac.id as id ,sum(case 
					   when coalesce(aml.amount_currency,0.00)<0.00 then 0.00 
					   else abs(coalesce(aml.amount_currency,0.00))
					  end) as debit_saldo_inicial,sum(case when coalesce(aml.amount_currency,0.00)>0.00 then 0.00 else abs(coalesce(aml.amount_currency,0.00)) end) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join 
		account_account_type acact on acact.id=acac.user_type_id 
		where
		acact.include_initial_balance<>True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id) as table_saldos_iniciales
		
		full outer join 
		
		(select acac.code as code,acac.name as name,acac.id as id,sum(case
                                           when coalesce(aml.amount_currency,0.00)<0.00 then 0.00
                                           else abs(coalesce(aml.amount_currency,0.00))
                                          end) as debit_movimiento_periodo,sum(case when coalesce(aml.amount_currency,0.00)>0.00 then 0.00 else abs(coalesce(aml.amount_currency,0.00)) end) 
				 	as credit_movimiento_periodo from
                account_move_line aml join
                account_account acac
                on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_account_type acact on acact.id=acac.user_type_id
                where
                am.state='posted' and
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id where
		abs(coalesce(table_saldos_iniciales.debit_saldo_inicial - table_saldos_iniciales.credit_saldo_inicial,0.00))>0.00 or
		table_movimientos_periodo.debit_movimiento_periodo >0.00 or
		table_movimientos_periodo.credit_movimiento_periodo >0.00
		order by code """ % (
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total

#######################################################################################################

def query_account_amount_balances_currency(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """select 
		case
		when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
		else table_saldos_iniciales.id 
		end id,
		case
		when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
		else table_saldos_iniciales.name 
		end,
		case 
		when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
		else table_saldos_iniciales.code 
		end code
		,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
		credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo from
		(select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit_currency) as debit_saldo_inicial,sum(aml.credit_currency) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_account_type acact on acact.id=acac.user_type_id where
		acact.include_initial_balance=True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		group by acac.id
		UNION
		select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit_currency) as debit_saldo_inicial,sum(aml.credit_currency) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_account_type acact on acact.id=acac.user_type_id where
		acact.include_initial_balance<>True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id) as table_saldos_iniciales
		full outer join 
		(select acac.code as code,acac.name as name,acac.id as id,sum(aml.debit_currency) as debit_movimiento_periodo,sum(aml.credit_currency) as credit_movimiento_periodo from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_account_type acact on acact.id=acac.user_type_id
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id order by code """ % (
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			
			"%s-01-01"%(inicio_anio),
			query_extras,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total

################################################################################################
###################### CONSULTAS DE PERIODO ####################################################

def query_account_amount_balances_with_period(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """select 
		case
		when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
		else table_saldos_iniciales.id 
		end id,
		case
		when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
		else table_saldos_iniciales.name 
		end,
		case 
		when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
		else table_saldos_iniciales.code 
		end code
		,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
		credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,
		table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo 
		from
		(select intermediate.id as id ,intermediate.code as code,intermediate.name as name,sum(intermediate.debit_saldo_inicial) as debit_saldo_inicial,
		sum(intermediate.credit_saldo_inicial) as credit_saldo_inicial 
		from (
		select acac.id as id ,acac.code as code,acac.name as name,sum(aml.debit) as debit_saldo_inicial,sum(aml.credit) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join 
		account_month_period apfy on apfy.id=aml.period_id where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s') and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id
		UNION
		select acac.id as id ,acac.code as code,acac.name as name,sum(aml.debit) as debit_saldo_inicial,sum(aml.credit) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join 
		account_month_period apfy on apfy.id=aml.period_id
		where 
		am.state='posted' and 
		aml.period_id in (select id from account_month_period where code='00/%s')
		group by acac.id) as intermediate group by id,code,name) as table_saldos_iniciales
		
		full outer join 
		
		(select acac.code as code,acac.name as name,acac.id as id,sum(aml.debit) as debit_movimiento_periodo,sum(aml.credit) as credit_movimiento_periodo 
		from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s') and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id
		where
		abs(coalesce(table_saldos_iniciales.debit_saldo_inicial - table_saldos_iniciales.credit_saldo_inicial,0.00))>0.00 or
		table_movimientos_periodo.debit_movimiento_periodo >0.00 or
		table_movimientos_periodo.credit_movimiento_periodo >0.00
		order by code """ % (
			inicio_anio,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			inicio_anio,
			inicio_anio,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total



def query_account_amount_balances_with_period_movements_cum(group_accounts,fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	query_total= """
		select sum(aml.balance) as balance_movimiento_periodo from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s') and 
		aml.date>='%s' and aml.date<='%s' %s and aml.account_id in %s  """ % (
			inicio_anio,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras,
			group_accounts_str)
		
	return query_total


def query_account_amount_balances_with_period_initial_balance_cum(group_accounts , fecha_movimiento_debe,query_extras):
	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total = """select sum(balance_inicial.balance) as balance_saldo_inicial from
		(select sum(aml.balance) as balance from
		account_move_line aml join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s' ) and 
		aml.date<'%s' and aml.date>='%s' %s and
		aml.account_id in %s 
		UNION
		select sum(aml.balance) as balance from
		account_move_line aml join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id
		where 
		am.state='posted' and 
		aml.period_id in (select id from account_month_period where code='00/%s' ) and
		aml.account_id in %s ) as balance_inicial""" % (
			inicio_anio,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			group_accounts_str,
			inicio_anio,
			group_accounts_str)

	return query_total


def query_account_amount_balances_with_period_currency(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """select 
		case
		when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
		else table_saldos_iniciales.id 
		end id,
		case
		when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
		else table_saldos_iniciales.name 
		end,
		case 
		when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
		else table_saldos_iniciales.code 
		end code
		,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
		credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo from
		(select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit_currency) as debit_saldo_inicial,sum(aml.credit_currency) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s') and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id
		UNION
		select acac.code as code,acac.name as name,acac.id as id ,sum(aml.debit_currency) as debit_saldo_inicial,sum(aml.credit_currency) as credit_saldo_inicial from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id
		where 
		am.state='posted' and 
		aml.period_id in (select id from account_month_period where code='00/%s')
		group by acac.id) as table_saldos_iniciales
		full outer join 
		(select acac.code as code,acac.name as name,acac.id as id,sum(aml.debit_currency) as debit_movimiento_periodo,sum(aml.credit_currency) as credit_movimiento_periodo from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_month_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (select id from account_month_period where code='00/%s') and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id order by code """ % (
			inicio_anio,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			inicio_anio,
			inicio_anio,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total
############################################################################################################################

def query_account_group_accounts(prefix_code):
	if prefix_code:
		len_account=len(prefix_code or '')
		query_total = """select acac.id, acac.code from account_account acac join account_group acgr on acgr.id=acac.group_id 
			where substring(acgr.code_prefix,1,%s) = '%s' """ %(len_account , prefix_code)
		return query_total