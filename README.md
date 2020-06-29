# django-wooah-logics-api-

<h1> 새로운플랫폼의 로직 </h1>

 Django를 이용하여 로직을 구성 , 중고거래라는 주제의 앱을준비 백엔드 부분

<h2> wooah 실행설명 </h2>

 1.모델을 설정하여(mysql과 연동) 테이블간의 관계를 정의한다.
 
 2.serializer를 이용하여 json파일로 쉽게 매핑. -오류를 에러를 내보내지 않고 컨트롤
 
 3.view에서 기능들을 구현한것을 포스트맨을 활용하여 테스트
 
 4.response_handler를 만들어 status code를 원하는 양식대로 컨트롤
 
 5.공공api를 이용하여 사용자들의 위치에 따른 location수집
 
 <h2>주요 기능</h2>
 
 1.상품 (CRUD)등록,수정,삭제,조회 기능구현
 
 2.회원정보 (CRUD)등록,수정,삭제,조회 기능
 
 3.상품의 이미지를 상품의 아이디와 외래키로연결하여 등록할수있도록 구현
 
 4.상품의 거래가 완료되었는지 구현
 
 5.위치정보를 가지고 올수있는 api 로직 구현 , 미리 데이터셋을 만들어놔서 get_or_create를 이용하여 없을시 생성 있을시 area 
 가지고온다.
 
 6.app_info를 init call로 날려 유저들의 플로우를 파악할수있는 데이터 수집
 
 7.약관동의 
 
 8.친구들을 등록할수있는 api 관계도 여기서 설정
 
 9.리뷰,상품의 거래내역,신고기능 구현
 
