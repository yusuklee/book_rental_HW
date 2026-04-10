class RecursiveDescentParser:
    def __init__(self, expr):
        # ── 입력 문자열을 토큰 리스트로 변환 ──
        # 예: "100 - 12 / 12"
        #   → [('num',100), '-', ('num',12), '/', ('num',12), '$']
        #
        # 숫자는 ('num', 실제값) 튜플로 저장
        # 연산자/괄호는 그냥 문자열로 저장
        # 끝에는 반드시 '$' 붙임 (입력 끝 표시)
        self.tokens = []
        num_tmp = ""
        for c in expr:
            if '0' <= c <= '9':
                num_tmp += c          # 연속된 숫자 문자 모으기
            else:
                if num_tmp:           # 숫자가 쌓여있으면 먼저 flush
                    self.tokens.append(('num', int(num_tmp)))
                    num_tmp = ""
                if c == ' ':
                    continue          # 공백은 무시
                if c in '+-*/()':
                    self.tokens.append(c)
        if num_tmp:                   # 마지막 숫자 flush
            self.tokens.append(('num', int(num_tmp)))
        self.tokens.append('$')

        self.pos  = 0   # 현재 읽고 있는 토큰 위치 (인덱스)
        self.step = 0   # 트레이스 출력 번호 (00, 01, 02, ...)

    def _peek(self):
        # 현재 토큰의 '타입'만 반환 (소비 X, 그냥 들여다보기만)
        # ('num', 100) → 'num'
        # '-'          → '-'
        t = self.tokens[self.pos]
        return t[0] if isinstance(t, tuple) else t

    def _remaining(self):
        # 트레이스 출력용: 아직 안 읽은 토큰들을 문자열로
        # ('num',100) → "num(100)", '-' → "-"
        parts = []
        for t in self.tokens[self.pos:]:
            if isinstance(t, tuple):
                parts.append(f"{t[0]}({t[1]})")
            else:
                parts.append(str(t))
        return ' '.join(parts)

    def _trace(self, msg):
        # 트레이스 한 줄 출력
        # (00) enter E                        | remaining input: num(100) - num(12) $
        print(f"({self.step:02d}) {msg:<35} | remaining input: {self._remaining()}")
        self.step += 1

    def parse(self):
        # 파싱 시작점. E() 호출 후 결과 리턴
        print("Tracing Start!!")
        result = self.E()
        self._trace("accept")
        return result

    # ────────────────────────────────────────────
    # 좌재귀 제거 후 문법:
    #   E  → T E'
    #   E' → + T E' | - T E' | ε
    #   T  → F T'
    #   T' → * F T' | / F T' | ε
    #   F  → ( E ) | num
    # ────────────────────────────────────────────

    def E(self):
        # E → T E'
        # 먼저 T 를 파싱하고, 그 결과를 E' 에 넘김
        self._trace("enter E")
        v = self.T()          # T 파싱 → 숫자값 반환
        v = self.E_prime(v)   # E' 파싱 → T 결과를 넘겨서 + - 누적
        self._trace(f"exit E => {v}")
        return v

    def E_prime(self, inh):
        # E' → + T E' | - T E' | ε
        #
        # inh = "이전까지 계산된 값" (inherited attribute)
        # 예: E_prime(100) → '+'를 보면 T 파싱 후 100+T 계산 → 재귀
        #                  → '+'/'-' 없으면 ε → inh 그대로 반환
        #
        # 왜 재귀로 구현?
        # 좌재귀를 제거하면 E' → + T E' 처럼 꼬리가 다시 E'로 이어짐
        # 이걸 재귀 호출로 표현
        self._trace("enter E'")
        t = self._peek()          # 다음 토큰 타입 확인 (소비 X)

        if t == '+':
            self.pos += 1         # '+' 소비
            self._trace("match '+'")
            rhs = self.T()        # + 오른쪽 T 파싱
            result = inh + rhs
            self._trace(f"compute: {inh} + {rhs} = {result}")
            return self.E_prime(result)   # 결과를 다시 E'에 넘김 (꼬리 처리)

        elif t == '-':
            self.pos += 1         # '-' 소비
            self._trace("match '-'")
            rhs = self.T()
            result = inh - rhs
            self._trace(f"compute: {inh} - {rhs} = {result}")
            return self.E_prime(result)

        else:
            # ε: + 도 - 도 없으면 그냥 inh 반환
            self._trace(f"E' -> epsilon, inherit {inh}")
            self._trace(f"exit E' => {inh}")
            return inh

    def T(self):
        # T → F T'
        # E 와 구조 동일. * / 를 + - 보다 먼저 처리 (우선순위)
        self._trace("enter T")
        v = self.F()
        v = self.T_prime(v)
        self._trace(f"exit T => {v}")
        return v

    def T_prime(self, inh):
        # T' → * F T' | / F T' | ε
        # E_prime 과 구조 동일, + - 대신 * /
        self._trace("enter T'")
        t = self._peek()

        if t == '*':
            self.pos += 1
            self._trace("match '*'")
            rhs = self.F()
            result = inh * rhs
            self._trace(f"compute: {inh} * {rhs} = {result}")
            return self.T_prime(result)

        elif t == '/':
            self.pos += 1
            self._trace("match '/'")
            rhs = self.F()
            result = inh // rhs    # 정수 나눗셈
            self._trace(f"compute: {inh} / {rhs} = {result}")
            return self.T_prime(result)

        else:
            # ε
            self._trace(f"T' -> epsilon, inherit {inh}")
            self._trace(f"exit T' => {inh}")
            return inh

    def F(self):
        # F → ( E ) | num
        # 가장 작은 단위: 숫자 하나 or 괄호로 감싼 표현식
        self._trace("enter F")
        t = self._peek()

        if t == '(':
            self.pos += 1         # '(' 소비
            self._trace("match '('")
            v = self.E()          # 괄호 안을 E 로 파싱
            self.pos += 1         # ')' 소비
            self._trace("match ')'")
            self._trace(f"exit F => {v}")
            return v

        else:  # num
            val = self.tokens[self.pos][1]   # ('num', 100) 에서 100 꺼냄
            self.pos += 1         # num 소비
            self._trace(f"match num -> {val}")
            self._trace(f"exit F => {val}")
            return val


# ── 테스트 ──
expr = "100 - 12 / 12"
parser = RecursiveDescentParser(expr)
result = parser.parse()
print("\nResult:", result)   # 99
