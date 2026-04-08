class SyntaxAnalyzer:
    def lexer(self, s):
        lexemes, tokens = [], []
        num_tmp = ""
        for one in s:
            if '0' <= one <= '9':
                num_tmp += one
            elif one==' ':
                continue
          
            else:
                if num_tmp:
                    lexemes.append(int(num_tmp))
                    tokens.append("num")
                    num_tmp = ""
                tokens.append(one)
                lexemes.append(one)
        if num_tmp:
            lexemes.append(int(num_tmp))
            tokens.append("num")
        lexemes.append("$")
        tokens.append("$")

        return lexemes, tokens

    def parser(self, lt):
        lexemes, tokens = lt

        # ─────────────────────────────────────────────
        # production 정의: (LHS, RHS 길이)
        # reduce할 때 RHS 길이만큼 stack pop 하기 위해 필요
        # ─────────────────────────────────────────────
        PROD = [
            ("E'", 1),  # 0: E' → E
            ('E', 3),  # 1: E → E + T
            ('E', 3),  # 2: E → E - T
            ('E', 1),  # 3: E → T
            ('T', 3),  # 4: T → T * F
            ('T', 3),  # 5: T → T / F
            ('T', 1),  # 6: T → F
            ('F', 3),  # 7: F → ( E )
            ('F', 1),  # 8: F → num
        ]

        # ─────────────────────────────────────────────
        # ★ 여기 두 dict를 너의 0번 표 보고 채우기 ★
        # ─────────────────────────────────────────────
        ACTION = {
            # (state, terminal): ('s', n)  → shift n
            # (state, terminal): ('r', k)  → reduce production k
            # (state, '$')     : ('acc',)  → accept
            #
            # 예시 (네 표의 state 번호에 맞게 수정):
            # (0, 'num'): ('s', 5),
            # (0, '('):   ('s', 4),
            # (1, '+'):   ('s', 6),
            # (1, '-'):   ('s', 7),
            # (1, '$'):   ('acc',),
            # (2, '+'):   ('r', 3),
            # (2, '*'):   ('s', 8),
            # ...
        }

        GOTO = {
            # (state, nonterminal): n
            #
            # 예시:
            # (0, 'E'): 1,
            # (0, 'T'): 2,
            # (0, 'F'): 3,
            # ...
        }

        # ─────────────────────────────────────────────
        # 파싱 루프 (아래는 건드릴 필요 없음)
        # ─────────────────────────────────────────────
        state_stack = [0]
        sym_stack = []  # 트레이스 표시용
        val_stack = []  # 실제 계산용
        ip = 0
        step = 0

        def fmt_stack():
            out = str(state_stack[0])
            for sy, st in zip(sym_stack, state_stack[1:]):
                out += f' {sy} {st}'
            return out

        def fmt_input():
            return ''.join(str(t) for t in tokens[ip:])

        # 헤더
        bar = '+------+------------------------------+----------------+----------------------+'
        print(bar)
        print('|      |            STACK             |     INPUT      |        ACTION        |')
        print(bar)

        while True:
            s = state_stack[-1]
            a = tokens[ip]

            if (s, a) not in ACTION:
                raise SyntaxError(f"unexpected token {a!r} at state {s}")

            act = ACTION[(s, a)]

            # 트레이스용 액션 문자열 만들기
            if act[0] == 's':
                action_str = f"Shift {act[1]}"
            elif act[0] == 'r':
                k = act[1]
                lhs, n = PROD[k]
                t_after_pop = state_stack[-1 - n] if n > 0 else state_stack[-1]
                action_str = f"Reduce {k} (Goto[{t_after_pop}, {lhs}])"
            else:  # 'acc'
                action_str = "Accept"

            # 한 줄 출력
            print(f'| ({step:02d}) |{fmt_stack():<30}|{fmt_input():>16}|{action_str:>22}|')
            step += 1

            # 실제 동작 수행
            if act[0] == 's':
                state_stack.append(act[1])
                sym_stack.append(a)
                val_stack.append(lexemes[ip])
                ip += 1

            elif act[0] == 'r':
                k = act[1]
                lhs, n = PROD[k]

                # 계산 (semantic action)
                if k == 1:
                    v = val_stack[-3] + val_stack[-1]  # E+T
                elif k == 2:
                    v = val_stack[-3] - val_stack[-1]  # E-T
                elif k == 3:
                    v = val_stack[-1]  # E→T
                elif k == 4:
                    v = val_stack[-3] * val_stack[-1]  # T*F
                elif k == 5:
                    v = val_stack[-3] // val_stack[-1]  # T/F (정수나눗셈)
                elif k == 6:
                    v = val_stack[-1]  # T→F
                elif k == 7:
                    v = val_stack[-2]  # F→(E)
                elif k == 8:
                    v = val_stack[-1]  # F→num

                # RHS 길이만큼 pop
                if n > 0:
                    del state_stack[-n:]
                    del sym_stack[-n:]
                    del val_stack[-n:]

                # LHS push + GOTO
                t = state_stack[-1]
                if (t, lhs) not in GOTO:
                    raise SyntaxError(f"no goto for {lhs} at state {t}")
                state_stack.append(GOTO[(t, lhs)])
                sym_stack.append(lhs)
                val_stack.append(v)

            else:  # 'acc'
                print(bar)
                return val_stack[-1]


S = SyntaxAnalyzer()
lexemes, tokens = S.lexer("100-12/12")
print("Lexemes:" + str(lexemes))
print("Tokens:" + str(tokens))








                    


