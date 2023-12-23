import psycopg2
import random

score ={'BRONZE':10, 'SILVER':20,'GOLD':30,'PLATINUM':40,'DIAMOND':50}

def get_id(cursor,table,column):
    query = f"SELECT MAX({column}) FROM {table}"
    cursor.execute(query)
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    return max_id

def printRecruitEnterprise():
    cursor.execute("select eid,e_name,scale,place from enterprise e where cut is not null order by eid")
    rows = cursor.fetchall()
    if rows:
        print("[모집공고 진행중인 기업 목록]")
        for row in rows:
            eid, e_name, scale, place = row
            print(f"ID: {eid}\t\t 이름: {e_name}\t\t기업 규모: {scale}\t\t위치: {place}\t\t")
        return True
    else:
        print("모집공고를 진행 중인 기업이 없습니다.")
        return False


def recruitment(cursor):
    while True:
        print("======================")
        print("1 : 기업 등록")
        print("2 : 모집공고 등록 ")
        print("3 : 모집공고 삭제")
        print("4 : 합격 발표")
        print("5 : 대회 개최")
        print("6 : 대회 결과")
        print("7 : 로그 아웃")
        print("======================")
        n = int(input())
        if n == 1:
            print("기업 이름 입력 >>", end="")
            name = input()
            print("기업 규모 입력 >>", end="")
            scale = input()
            print("기업 위치 입력 >>", end="")
            place = input()
            eid = get_id(cursor,"enterprise","eid")+1

            cursor.execute("insert into enterprise (eid,e_name,scale,place) values(%s, %s, %s, %s)", (eid, name, scale,place))
            cursor.connection.commit()
        elif n == 2:
            cursor.execute("select eid,e_name,scale,place from enterprise e where cut is null order by eid")
            rows = cursor.fetchall()
            if rows:
                print("[모집공고 예정 기업 목록]")
                for row in rows:
                    eid,e_name,scale,place = row
                    print(f"ID: {eid}\t\t 이름: {e_name}\t\t기업 규모: {scale}\t\t위치: {place}\t\t")
                print("공고를 등록할 기업 ID >>", end="")
                eid = int(input())
                print("요구하는 최소 코딩테스트 점수 >>", end="")
                cut = int(input())
                cursor.execute("update enterprise set cut = %s where eid = %s",(cut,eid))
                cursor.connection.commit()
                print("입력이 완료되었습니다")
            else:
                print("모집공고를 올린 기업이 없습니다.")
        elif n == 3:
            if printRecruitEnterprise():
                print("공고를 삭제할 기업 ID >>", end="")
                eid = int(input())
                cursor.execute("update enterprise set cut = NULL where eid = %s", (eid,))
                cursor.connection.commit()
                print("삭제가 완료되었습니다")
        elif n == 4:
            if printRecruitEnterprise():
                print("합격을 발표할 기업 ID >>", end="")
                eid = int(input())

                cursor.execute("select sid,eid,position,point from job_interview ji natural join problemsolver p natural join enterprise e where ji.eid =%s and cut <= point or sid in (select sid from contest natural join contest_participants cp where rank <=3 and eid = ji.eid)",(eid,))
                #기업에서 주최한 대회에서 3등안에 들거나 OR 기업의 컷을 넘긴 지원자를 뽑는다.
                rows = cursor.fetchall()
                for row in rows:
                    sid, eid, position,point = row
                    cursor.execute("insert into programmer (sid, eid, position, salary) values(%s, %s, %s, %s)",(sid,eid,position,point*10000))
                    #코테 점수 * 10000원
                cursor.connection.commit()


        elif n == 5:
            print("대회 이름 입력 >>", end="")
            name = input()
            print("상금 입력 >>", end="")
            prize = input()
            cursor.execute("select eid,e_name from enterprise e order by eid")
            rows = cursor.fetchall()
            if rows:
                print("[대회를 개최할 기업 목록]")
                for row in rows:
                    eid, e_name= row
                    print(f"ID: {eid}\t\t 이름: {e_name}\t\t")
                print("개최할 기업의 ID 입력 >>", end="")
                eid = int(input())

                contest_id = get_id(cursor, "contest", "contest_id") + 1
                cursor.execute("insert into contest (contest_id, eid, contest_name,prize) values(%s, %s, %s, %s)",(contest_id, eid, name,prize))
                cursor.connection.commit()
                print("입력이 완료되었습니다")
            else: print("기업이 없습니다")

        elif n == 6:
            cursor.execute("select distinct(contest_id),contest_name from contest_participants cp natural join contest where rank is null order by contest_id")
            # 발표가 나지 않은 콘테스트 출력 rank가 null인 distinct한 contest_id
            rows = cursor.fetchall()
            if rows:
                print("[결과가 나지 않은 대회 목록]")
                for row in rows:
                    contest_id, contest_name= row
                    print(f"ID: {contest_id}\t\t 이름: {contest_name}\t\t")
                print("결과를 발표할 대회의 ID 입력 >>", end="")
                contest_id = int(input())
                cursor.execute("select sid from contest_participants natural join problemsolver p where contest_id = %s order by point desc,gpa desc",(contest_id,))
                # 코테 점수/ 그후 학점순으로 desc (내림차순) 으로 정렬하고 그 순서대로 sid를 가져온다.
                rows = cursor.fetchall()
                rank = 1
                for row in rows:
                    sid = row
                    cursor.execute("update contest_participants set rank = %s where sid = %s",(rank,sid))
                    rank += 1
                cursor.connection.commit()
                print("대회 결과가 발표되었습니다.")
            else: print("발표할 대회가 없습니다")
        elif n == 7:
            print("로그 아웃")
            break
        else:
            print("잘못 입력하셨습니다.")

def quesionAnswer():
    print("======================")
    print("1 : 질문 등록")
    print("2 : 질문 답변 ")
    print("3 : 게시판 조회")
    print("======================")
    n = int(input())
    if n == 1:
        cursor.execute("select sid,pid,name from solve natural join problemsolver except select sid,pid,name from solve natural join problemsolver where success = 1")
        # success하지 못한 sid,pid
        rows = cursor.fetchall()
        if rows:
            print("[Solver가 틀린 문제 목록]")
            for row in rows:
                sid,pid,name = row
                print(f"ID: {sid}\t\t 이름: {name}\t\t문제 번호: {pid}\t\t")
            print("질문 등록할 Solver의 id 입력 >>", end="")
            sid = int(input())
            print("질문 등록할 Problem의 id 입력 >>", end="")
            pid = int(input())
            post_id = get_id(cursor,"question_answer","post_id")+1
            cursor.execute("insert into question_answer (post_id,qid,pid) values(%s, %s, %s)", (post_id, sid, pid))
            cursor.connection.commit()
        else:
            print("틀린 문제가 없습니다")
    elif n == 2:
        cursor.execute("select post_id,pid,name from question_answer q join problemsolver p on q.qid = p.sid  where resolve is NULL order by post_id")
        #해결하지 못한 문제의 post_id, pid, name을 JOIN을 이용해 가져온다.
        rows = cursor.fetchall()
        if rows:
            print("[미해결 문제 목록]")
            for row in rows:
                post_id,pid,name = row
                print(f"{post_id}\t 질문자: {name}\t\t문제 번호: {pid}\t\t")
            print("해결할 post_id 입력 >>", end="")
            post_id = int(input())
            cursor.execute(
                "select distinct(sid),name from solve natural join problemsolver where pid = (select pid from question_answer where post_id = %s) and success = 1 order by sid",
                (post_id,))
            rows = cursor.fetchall()
            if rows:
                print("[해당 문제를 Solve한 Solver]")
                for row in rows:
                    sid, name = row
                    print(f"ID: {sid}\t 해결자 {name}")
                print("응답할 Solver의 ID 입력 >>", end="")
                rid = int(input())
                resolve = random.choice([0, 1])
                cursor.execute("update question_answer set rid = %s,resolve = %s where post_id = %s",
                               (rid, resolve, post_id))
                cursor.connection.commit()
                if resolve:
                    print("□■□■□■□■□■□■ 해결완료 □■□■□■□■□■□■")
                else:
                    print("□■□■□■□■□■□■ 해결실패 □■□■□■□■□■□■")
            else:
                print("문제를 해결한 Solver가 없습니다.")
        else: print("미해결된 문제가 없습니다.")


    elif n == 3:
        cursor.execute("select post_id,p.name as qname,p2.name as rname ,pid,title,resolve from question_answer q left join problemsolver p on q.qid = p.sid left join problemsolver p2 on q.rid = p2.sid natural join problem order by post_id")
        #post_id, qname, rname, pid, title, resolve
        rows = cursor.fetchall()
        if rows:
            print("[질의응답 게시판]")
            for row in rows:
                post_id, qname, rname, pid, title, resolve = row
                if rname is None: rname = "[  ]"
                if resolve is None: resolve = "진행 중"
                elif resolve == 0: resolve = "해결 실패"
                elif resolve == 1 : resolve = " 해결 완료"
                print(f"ID: {post_id}\t\t 질문자: {qname}\t\t 응답자: {rname}\t\t 문제: [{pid}] {title}\t\t{resolve}")
        else: print("게시판에 글이 없습니다")
def solver():
    while True:
        print("======================")
        print("1 : Solver 추가")
        print("2 : Solver 삭제 ")
        print("3 : 문제 풀기")
        print("4 : 질의 응답 ")
        print("5 : 응시자 스펙 조회")
        print("6 : 모집 공고 지원")
        print("7 : 합격자 조회")
        print("8 : 대회 지원")
        print("9 : 대회 결과 조회")
        print("10 : 강의 수강")
        print("11 : 학원 등록")
        print("12 : 로그 아웃")
        print("======================")
        n = int(input())
        if n == 1:
            insert_solver(cursor)
        elif n == 2:
            delete_solver(cursor)
        elif n == 3:
            solve()
        elif n == 4:
            quesionAnswer()
        elif n == 5:
            view_solver(cursor)

        elif n == 6:
            if view_solver(cursor):
                print("선택할 Solver의 ID 입력 >>", end="")
                sid = int(input())
                cursor.execute("select eid,e_name from enterprise e where cut is not null order by eid")
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        eid, name = row
                        print(f"ID: {eid}\t\t기업: {name}")
                    print("지원 할 기업의 ID 입력 >>", end="")
                    eid = int(input())
                    print("지원 할 직무 입력 >>", end="")
                    position = input()
                    cursor.execute("select iid from instructor i order by iid")
                    results = cursor.fetchall()
                    if results:
                        iids = [int(result[0]) for result in results]   #iid 리스트로 받아온다.
                        iid = random.choice(iids)
                        # 면접관중 한명 랜덤으로 뽑음
                        cursor.execute("insert into job_interview (sid,eid,iid,position) values(%s, %s, %s, %s)",(sid,eid,iid,position))
                        cursor.connection.commit()
                        print("회사에 지원하셨습니다.")
                    else:
                        print("강사를 추가해야 합니다.")
                else:
                    print("기업이 없습니다, 기업을 추가해 주세요.")


        elif n == 7:
            cursor.execute("select name, e_name, position ,salary  from programmer natural join problemsolver p natural join enterprise e")
            rows =cursor.fetchall()
            if rows:
                print("[합격자]")
                idx = 1
                for row in rows:
                    name, e_name, position, salary = row
                    print(f"ID: {idx}\t\t이름: {name}\t\t회사: {e_name}\t\t직무: {position}\t\t급여: {salary}\t\t")
                    idx +=1
            else: print("합격자가 없습니다")
        elif n == 8:
            cursor.execute("select contest_id , contest_name , prize, e_name from contest c natural join enterprise e order by contest_id")
            rows = cursor.fetchall()
            if rows:
                print("[모집중인 대회]")
                for row in rows:
                    contest_id, contest_name, prize, e_name = row
                    print(f"ID: {contest_id}\t\t이름: {contest_name}\t\t주최: {e_name}\t\t상금: {prize}\t\t")
                print("지원할 대회의 ID 입력 >>", end="")
                contest_id = int(input())
                view_solver(cursor)
                print("지원할 Solver의 ID 입력 >>", end="")
                sid = int(input())
                cursor.execute("insert into contest_participants (contest_id ,sid,rank) values(%s, %s, null)",(contest_id,sid))
                cursor.connection.commit()
                print("대회에 참가하였습니다.")
            else: print("모집중인 대회가 없습니다.")

        elif n == 9:
            cursor.execute("select distinct(contest_id)as id, contest_name,e_name from contest_participants natural join contest natural join enterprise where rank is not null")
            #결과가 발표된 대회 가져온다
            rows = cursor.fetchall()
            if rows:
                print("[발표된 대회]")
                for row in rows:
                    id, contest_name, e_name = row
                    print(f"ID: {id}\t\t이름: {contest_name}\t\t주최: {e_name}\t\t")
                print("결과를 조회할 대회의 ID 입력 >>", end="")
                contest_id = int(input())
                cursor.execute("select rank,name from contest_participants natural join problemsolver where contest_id = %s order by rank",(contest_id,))
                rows = cursor.fetchall()
                print("[시상]")
                print("======================")
                for row in rows:
                    rank, name = row
                    if rank == 1: print(f"[금상]\t\t이름: {name}\t\t")
                    elif rank == 2 : print(f"[은상]\t\t이름: {name}\t\t")
                    elif rank == 3: print(f"[동상]\t\t이름: {name}\t\t")
                    else: print(f"{rank}등\t\t이름: {name}\t\t")
                print("======================")
            else: print("결과가 발표된 대회가 없습니다")
        elif n == 10:
            cursor.execute("select iid, i_name, pid, title from problem_lecture natural join instructor natural join problem")
            rows = cursor.fetchall()
            if rows:
                print("[강의 목록]")
                for row in rows:
                    iid, i_name, pid, title = row
                    print(f"ID: {iid}\t\t강사: {i_name}\t\t문제: [{pid}] {title}\t\t")
                print("강사 ID 입력 >>", end="")
                iid = int(input())
                print("문제 ID 입력 >>", end="")
                pid = int(input())
                cursor.execute("select distinct(sid), name from solve natural join problemsolver p  where pid = %s and success = 0",(pid,))
                rows = cursor.fetchall()
                print("[틀린 학생 목록]")
                if rows :
                    for row in rows:
                        sid, name = row
                        print(f"ID: {sid}\t\t이름: {name}\t\t")
                    print("수강할 Solver ID 입력 >>", end="")
                    sid = int(input())
                    cursor.execute("insert into lecture_student (iid ,pid, sid) values(%s, %s, %s)",(iid,pid,sid))
                    cursor.connection.commit()
                    print("강의 수강이 완료되었습니다")
                else:
                    print("틀린 Solver가 없습니다")
            else: print("등록된 강의가 없습니다")
        elif n == 11:
            cursor.execute("select eiid, name, i_name from educational_institute ei join instructor i on i.iid = ei.ceo_id")
            # 학원 정보 출력
            rows = cursor.fetchall()
            if rows:
                print("[학원 정보]")
                for row in rows:
                    eiid, name, i_name = row
                    print(f"ID: {eiid}\t\t학원 이름: {name}\t\t대표 원장: {i_name}\t\t")
                print("학원 번호 >>", end="")
                eiid = int(input())
                cursor.execute("select sid,name from problemsolver s where sid not in (select sid from institute_student where eiid = %s) order by sid",(eiid,))
                # 현재 학원에 다니지 않는 학생 선택
                rows = cursor.fetchall()
                if rows:
                    print("[학원에 다닐 학생 선택]")
                    for row in rows:
                        sid, name = row
                        print(f"ID: {sid}\t\t학생: {name}\t\t")
                    print("학생 번호 >>", end="")
                    sid = int(input())
                    cursor.execute("insert into institute_student(eiid,sid) values(%s,%s)", (eiid, sid))
                    cursor.connection.commit()
                    print("학원에 학생이 등록되었습니다.")
                else: print("학원에 다니지 않는 학생이 없습니다")
            else: print("등록된 학원이 없습니다")
        elif n == 12:
            print("로그 아웃")
            break
        else: print("잘못 입력하셨습니다.")


def solve():
    if view_solver(cursor):
        print("코딩 테스트를 응시할 Solver의 id를 입력 >>",end="")
        sid = int(input())
        cursor.execute("select name from problemsolver where sid = %s",(sid,))
        name = cursor.fetchone()[0]
        print(f"[{name}] 님을 선택하였습니다.")
        if view_problem(cursor):
            print("풀 문제의 번호 >>",end="")
            pid = int(input())

            ssid = get_id(cursor,"solve","ssid")+1;
            success = random.choice([0, 1])
            cursor.execute("insert into solve (ssid,sid,pid,success) values(%s, %s, %s, %s)",(ssid, sid, pid, success))

            cursor.execute("select sid, point, name, pid,tier,title,success from solve natural join problemsolver natural join problem where ssid = %s",(ssid,))
            sid, point, name, pid, tier, title, suc = cursor.fetchone()
            if suc:
                print()
                print("□■□■□■□■□■□■ 축하합니다 □■□■□■□■□■□■")
                print(f"{name} solve the [{pid}] {title} ")
                print("□■□■□■□■□■□■ 축하합니다 □■□■□■□■□■□■")
                print(score[tier],"점 획득")
                print()
                cursor.execute("update problemsolver set point = %s where sid = %s",(point+score[tier],sid))
            else:
                print()
                print(f"{name} failed to solve the [{pid}] {title} ")
                print("Try Again ~")
                print()
            cursor.connection.commit()


def instructor():
    while True:
        print("======================")
        print("1 : 강사 등록")
        print("2 : 강의 등록")
        print("3 : 수강 학생 조회 ")
        print("4 : 학원 창립")
        print("5 : 학원 취원")
        print("6 : 학원 조회")
        print("7 : 문제 만들기")
        print("8 : 로그 아웃")
        print("======================")
        n = int(input())
        if n == 1:
            print("삽입할 Instructor의 정보를 입력 >>")
            iid = get_id(cursor, "instructor", "iid") + 1  # 다음 ID 받아옴
            print("이름 >>", end="")
            name = input()
            print("코딩 실력 >>", end="")
            point = int(input())
            print("급여 >>", end="")
            salary = int(input())
            cursor.execute("insert into instructor (iid,i_name,point,salary) values(%s, %s, %s, %s)",(iid, name, point, salary))
            cursor.connection.commit()
            print("Instructor가 입력되었습니다.")
        elif n == 2:
            cursor.execute("select pid, title from problem order by pid ")
            rows = cursor.fetchall()
            if rows:
                print("[강의로 찍을 문제 목록]")
                for row in rows:
                    pid, title = row
                    print(f"ID: {pid}\t\t제목: {title}\t\t")
                print("문제 번호 >>", end="")
                pid = int(input())
                cursor.execute("select iid, i_name from instructor order by iid")
                rows = cursor.fetchall()
                if rows:
                    print("[강의를 찍을 강사 목록]")
                    for row in rows:
                        iid,i_name = row
                        print(f"ID: {iid}\t\t강사: {i_name}\t\t")
                    print("강사 번호 >>", end="")
                    iid = int(input())
                    cursor.execute("insert into problem_lecture (iid,pid) values(%s, %s)",(iid,pid))
                    print("강의가 등록되었습니다")
                    cursor.connection.commit()
                else: print("강의를 찍을 강사가 없습니다, 강사를 등록 해 주세요")
            else: print("강의를 찍을 문제가 없습니다, 문제를 등록 해 주세요")
        elif n == 3:
            cursor.execute("select i_name,name,pid,title from lecture_student ls natural join problemsolver natural join problem join instructor i on ls.iid = i.iid")
            #강사의 수업을 수강하는 학생과 연결
            rows = cursor.fetchall()
            if rows:
                print("[강사와 수강 학생 목록]")
                idx =1
                for row in rows:
                    i_name,name,pid,title = row
                    print(f"{idx}: 강사: {i_name}\t\t학생: {name}\t\t문제: [{pid}] {title}\t\t")
                    idx += 1
            else: print("강의와 수강하는 학생이 없습니다.")
        elif n == 4:
            eiid = get_id(cursor,"educational_institute","eiid") + 1
            print("학원 이름 >>", end="")
            name = input()
            cursor.execute("select iid,i_name from instructor i where iid not in (select distinct(ceo_id) from educational_institute) order by iid")
            #ceo가 아닌 강사 조회
            rows = cursor.fetchall()
            if rows:
                print("[대표 강사 선택]")
                for row in rows:
                    iid, i_name = row
                    print(f"ID: {iid}\t\t강사: {i_name}\t\t")
                print("강사 번호 >>", end="")
                iid = int(input())
                cursor.execute("insert into educational_institute(eiid,name,ceo_id) values(%s,%s, %s)", (eiid,name,iid))
                cursor.connection.commit()
                print("학원이 창립되었습니다")
            else : print("대표강사를 정할 수 없습니다")
        elif n == 5:
            cursor.execute("select eiid, name, i_name from educational_institute ei join instructor i on i.iid = ei.ceo_id")
            #학원 정보 출력
            rows = cursor.fetchall()
            if rows:
                print("[학원 정보]")
                for row in rows:
                    eiid,name,i_name = row
                    print(f"ID: {eiid}\t\t학원 이름: {name}\t\t대표 원장: {i_name}\t\t")
                print("학원 번호 >>", end="")
                eiid = int(input())
                cursor.execute("select iid, i_name from instructor i where iid not in (select iid from institute_instructor where eiid = %s)",(eiid,))
                #현재 학원에 근무하지 않는 강사 선택
                rows = cursor.fetchall()
                if rows:
                    print("[근무할 강사 선택]")
                    for row in rows:
                        iid, i_name = row
                        print(f"ID: {iid}\t\t강사: {i_name}\t\t")
                    print("강사 번호 >>", end="")
                    iid = int(input())
                    cursor.execute("insert into institute_instructor(eiid,iid) values(%s,%s)", (eiid, iid))
                    cursor.connection.commit()
                    print("학원에 강사가 등록되었습니다.")
                else: print ("학원에 근무할 강사가 없습니다.")
            else: print("학원이 없습니다. 학원을 창립해주세요.")
        elif n == 6:
            cursor.execute("select ei.eiid, name,count(distinct ii.iid) as instructorcnt, count(distinct id.sid) as solvercnt from educational_institute ei left join institute_instructor ii on ei.eiid = ii.eiid left join institute_student id on ei.eiid = id.eiid group by ei.eiid order by eiid ")
            #학원의 이름,강사 수, 응시자 수 반환
            rows = cursor.fetchall()
            if rows:
                print("[학원 현황 조회]")
                for row in rows:
                    eiid, name,instructorcnt,solvercnt  = row
                    print(f"ID: {eiid}\t\t학원 이름: {name}\t\t강사 수: {instructorcnt}\t\t수강생 수: {solvercnt}\t\t")
            else: print("학원이 없습니다. 학원을 창립해주세요.")
        elif n == 7:
            print("등록할 문제 번호 >>", end="")
            pid = int(input())
            print("문제 제목 >>", end="")
            title = input()
            print("알고리즘 유형 >>", end="")
            algorithm = input()
            print("티어 [bronze, silver, gold, platinum, diamond] >>", end="")
            tier = input().upper()  #대문자로 변경
            print("레벨 [1~5] >>", end="")
            level = int(input())
            cursor.execute("insert into problem(pid,title,algorithm,tier,tier_num) values(%s,%s,%s,%s,%s)", (pid, title,algorithm,tier,level))
            cursor.connection.commit()
            print("문제가 등록되었습니다")
        elif n == 8:
            print("로그 아웃")
            break
        else : print("잘못 입력하셨습니다.")


def view_problem(cursor):
    cursor.execute("select * from problem order by algorithm")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            pid, title, algorithm, tier, tier_num = row
            print(f"{pid}\t\t제목: {title}\t\t유형: {algorithm}\t\t티어: {tier}-{tier_num}")
        return True
    else:
        print("문제가 없습니다.")
        return False

def view_solver(cursor):
    cursor.execute("select * from problemsolver order by sid")
    rows = cursor.fetchall()
    if rows:
        print("======================")
        for row in rows:
            sid, name, point, gpa, school = row
            print(f"{sid}\t\t이름: {name}\t\t코딩: {point}\t\t학점: {gpa}\t\t학교: {school}")
        print("======================")
        return True
    else:
        print("Solver가 없습니다")
        return False
def delete_solver(cursor):
    if view_solver(cursor):
        print("삭제할 Solver의 id 값을 입력 >>",end="")
        id = int(input())
        mxid = get_id(cursor,"problemsolver","sid")
        if 1<= id <= mxid:
            cursor.execute("DELETE FROM problemsolver where sid = %s",(id,))
            cursor.connection.commit()
            print("Solver가 삭제되었습니다.")
        else:
            print("잘못된 ID를 입력하였습니다.")

def insert_solver(cursor):
    print("삽입할 Solver의 정보를 입력 >>")
    id = get_id(cursor,"problemsolver","sid")+1     #다음 ID 받아옴
    print("이름 >>",end="")
    name = input()
    print("학점 >>",end="")
    gpa = input()
    print("학교 >>",end="")
    school = input()
    cursor.execute("insert into problemsolver (sid,name,point,gpa,school) values(%s, %s, 0, %s, %s)",(id,name,gpa,school))
    cursor.connection.commit()
    print("Solver가 입력되었습니다.")

def run():
    while True:
        print("======================")
        print("ROLE을 선택하세요")
        print("[1: solver  2: enterprise  3: instructor]")
        print("======================")
        n= int(input())
        if n == 1:
            cursor.execute("set role solver")
            print("Solver로 로그인 하셨습니다.")
            solver()
        elif n == 2:
            cursor.execute("set role enterprise")
            print("Enterprise로 로그인 하셨습니다.")
            recruitment(cursor)
        elif n == 3:
            cursor.execute("set role instructor")
            print("Instructor로 로그인 하셨습니다.")
            instructor()
        cursor.execute("reset role")    # role 초기화


if __name__ == '__main__':
    con = psycopg2.connect(
        database ='sample2023',
        user ='db2023',
        password='db!2023',
        host='::1',
        port ='2108'
    )
    cursor = con.cursor()
    while True:
        run()






