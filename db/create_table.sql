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
)

create table errors (
	id serial not null primary key,
	codigoexec text not null,
	codigo text not null,
	msg text not null
)

create table rendimento (
	id serial not null primary key,
	fii integer REFERENCES fii(id),
	dtpagamento date not null,
	cotacao float not null,
	rendimento float not null
)
