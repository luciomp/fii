create table fii (
	id serial not null primary key,
	codigoexec text not null,
	url text not null,
	codigo text not null,
	nome text,
	tipo text not null,
	subtipo text not null,
	dtregistrocvm date,
	cotas int not null,
	cotistas int not null,
	notas text,
	taxas text,
	dy float,
	ultimorendimento float,
	pl numeric,
	vpa float,
	cotacao float,
	pvpa float
);

create table errors (
	id serial not null primary key,
	codigoexec text not null,
	codigo text not null,
	msg text not null
);

create table rendimento (
	id serial not null primary key,
	fii integer REFERENCES fii(id),
	dtpagamento date not null,
	cotacao float not null,
	rendimento float not null
);

CREATE OR REPLACE VIEW rendimentoultimos10meses AS
	select
		fii.id as id,
		sum(rendimento.rendimento)/fii.cotacao as dy
	from
		fii
	inner join
		rendimento on fii.id = rendimento.fii
	where
		dtpagamento > now() - interval '10 months'
	group by fii.id;

CREATE VIEW rendimentoano AS
	select
		fii.id as id,
		sum(rendimento.rendimento)/fii.cotacao as dy
	from
		fii
	inner join
		rendimento on fii.id = rendimento.fii
	where
		extract('year' from dtpagamento) = extract('year' from now())
	group by
		fii.id;

create view amplituderendimento AS
	select
		fii.id as id,
		(max(rendimento) - avg(rendimento)) / avg(rendimento) as Ma,
		(avg(rendimento) - min(rendimento)) / avg(rendimento) as Mi
	from
		fii
	inner join
		rendimento on fii.id = rendimento.fii
	group by
		fii.id;

create view fiiultimaexec AS
    select
	    codigo, tipo, subtipo, cotacao,
	    round(fii.dy::numeric, 2) as dy,
	    round(rendimentoultimos10meses.dy::numeric*100, 2) as dy10m,
	    round(rendimentoano.dy::numeric*100, 2) as dyano,
	    round(pvpa::numeric, 2) as pvpa,
        amplituderendimento.Ma,
        amplituderendimento.Mi,
	    url,
	    notas
    from
	    fii
    inner join
	    rendimentoultimos10meses on fii.id = rendimentoultimos10meses.id
    inner join
	    rendimentoano on fii.id = rendimentoano.id
    inner join
	    amplituderendimento on fii.id = amplituderendimento.id
    where
	    codigoexec = (select max(codigoexec) from fii)
    order by
	    codigo;
