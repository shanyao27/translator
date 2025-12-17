program test_strings;

var
    firstName: string;
    lastName: string;
    fullName: string;
    greeting: string;

function concat_strings(a: string; b: string): string;
begin
    concat_strings := a + b;
end;

function hello(name: string): string;
begin
    hello := 'Hello, ' + name;
end;

begin
    firstName := 'Nikita';
    lastName := ' Vdovenkov';

    fullName := concat_strings(firstName, lastName);
    greeting := hello(fullName);

    writeln('Full name: ', fullName);
    writeln(greeting);
end.