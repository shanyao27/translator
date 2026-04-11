program OopTest;

type
  TCounter = class
    Value: integer;
    constructor Create(v: integer);
    procedure Increment;
    function GetValue: integer;
  end;

var
  c: TCounter;

constructor TCounter.Create(v: integer);
begin
  Value := v
end;

procedure TCounter.Increment;
begin
  Value := Value + 1
end;

function TCounter.GetValue: integer;
begin
  GetValue := Value
end;

begin
  c := TCounter.Create(0);
  c.Increment;
  c.Increment;
  c.Increment;
  writeln(c.GetValue())
end.
