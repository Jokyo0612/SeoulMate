import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json

import functions

with st.spinner('경로 계산 중입니다...'):

# API 키 바꾸기
  client = OpenAI(
      api_key="OPENAI_API_KEY"
  )

  # 방문지 좌표 (이후 좌표 받아오기)
  if 'dic' not in st.session_state:
     st.session_state.dic = {}
  visit_dict = st.session_state.dic

  print(visit_dict)

  # visit_dict = {
  #   "고려대학교": (37.5891, 127.0324),
  #   "홍대입구": (37.5571, 126.9243),
  #   "서울랜드" : (37.4341, 127.0204),
  #   "롯데월드": (37.5110, 127.0981),
  #   "롯데월드 아쿠아리움": (37.5135, 127.104919)
  # }

  # make list and str
  visit_list = []
  for i in visit_dict:
    visit_list.append(i)
  
  print(visit_list)

  str_visit = ""
  for element in visit_list:
    str_visit += element + ','


  # LLM으로 최적 경로 추출
  completions = client.chat.completions.create(
      model = "gpt-4o-mini",
      messages = [
          {"role" : "user", "content" : (
                  "내가 방문지 리스트를 줄건데 리스트의 장소를 오늘 하루 동안 돌아다닐 예정이야."
                  "방문 순서를 거리와 방문지 설명, 추천 활동, 방문지 오픈 시간을 고려해서 계획을 만들어줄래? "
                  "방문 순서 답변 포멧은 다음과 같아, 방문지 리스트에 있는 장소 이름만 나열해줘"
                  "별도의 설명이나 주석은 작성하지마"
                  "방문지 순서 : 장소 이름/장소 이름/장소 이름/장소 이름/장소 이름"\
                  "방문지 리스트 : " + str_visit
              )
          }
      ]
  )


                  # "그외 답변 정보 양식은 다음과 같아: "
                  # "1. 방문지 이름\n"
                  # "   - 오픈 시간 : (오픈 시간)\n"
                  # "   - 오픈 요일 : (오픈 요일)\n"
                  # "   - 추천 체류 : N시간\n"
                  # "   - 추천 활동 : (추천 활동)\n"
                  # "   - 방문지 설명 : (방문지 설명)"


  # 방문지 경로 순서 별 좌표 나열
  message = (completions.choices[0].message.content).strip("방문지 순서 : ")
  v_list = message.split('/')
  visit_vector = []

  for j in v_list:
    visit_vector.append(visit_dict[j])

  # 전체 맵
  maxLat=0
  maxLng=0
  minLat=0
  minLng=0
  count = 0
  for each in visit_vector: #내가 추가한 코드
    maxLat += each[0]
    maxLng += each[1]
    count +=1
  c_lat = (maxLat) / count
  c_lng = (maxLng) / count
  center = {'lat': c_lat, 'lng':c_lng}
  # 1


  # 경로 Json 파일 출력
  g_api_key = "G_API_KEY"  # Google Maps API 키
  route_info = []

  # 전체 맵
  total_json = dict() #내가 추가한 코드

  for le in range(len(visit_vector)-1):
    route = functions.compute_routes(g_api_key, visit_vector[le], visit_vector[le+1])
    route_info.append(route)
    total_json[le] = route #내가 추가한 코드


  # 도보 거리 계산
  opsr_api_key = "OPSR_API_KEY"  # OpenRouteService API 키

  for le in range(len(visit_vector)-1):
    walkRoute = functions.get_walking_directions(opsr_api_key, visit_vector[le], visit_vector[le+1])
    if route_info[le]['routes'][0]['legs'][0]['distance']['value'] < 400: #> walkRoute['routes'][0]['summary']['duration']:
       route_info[le] = json.loads(functions.make_json(walkRoute))
       total_json[le] = route_info[le]
       

  #     stroute1 = json.dumps(walkRoute, ensure_ascii=False)
  #     stroute2 = json.dumps(route_info[le], ensure_ascii=False)
      
  #     completions2 = client.chat.completions.create(
  #         model = "gpt-4o-mini",
  #         messages = [
  #             {"role" : "user", "content" : (
  #                     "내가 주는 파일 1번을 2번의 형태로 변환시켜줘. 1번 : " + stroute1\
  #                       + "2번 : "+ stroute2 + "변환하는 과정에서 채울 수 없는 데이터는 None 대신 1을 넣어줘"\
  #                       "비어있는 문자열은 주어진 좌표를 바탕으로 입력해줘"\
  #                       "polyline은 구글 맵에서 사용하는 polyline code니까 참고해서 데이터를 채워줘"\
  #                       "별도의 부가 설명이나 주석을 추가하지 말고 변환된 파일만 보내줘"
  #                       "앞에 {\"\"\"json} 이랑 뒤에{\"\"\"} 도 붙이지 마"
  #                 )
  #             }
  #         ]
  #     )
  #     print(completions2.choices[0].message.content)
  #     route_info[le] = json.loads(completions2.choices[0].message.content)
  #     # route_info[le] = completions2.choices[0].message.content
  #     # print(route_info[le])
  total_json['center'] = center
  st.success("계산이 끝났습니다!")


# streamlit UI
st.title('여행 경로를 확인하세요')
st.sidebar.info(body='Route Detail')
num_expanders = len(route_info)

if 'selected_route_all' not in st.session_state:
    st.session_state.selected_route_all = total_json

for i in range(len(route_info)):
    key = f'selected_route_{i}'
    if key not in st.session_state:
        st.session_state[key] = route_info[i]

# 선택된 경로가 있으면 지도를 업데이트합니다.
if st.session_state.selected_route_all:
  html_with_json = functions.map_call2(st.session_state.selected_route_all)

# 사이드바에 동적으로 expander 생성
for a in range(len(route_info)):
    shortName = st.session_state[f'selected_route_{a}']["routes"][0]["legs"][0]["steps"]
    stepsCount = len(shortName)
    with st.sidebar.expander(f'route {a+1}'):
      for b in range(stepsCount):
          if(shortName[b]['travel_mode']=="WALKING"):
              st.write(shortName[b]['html_instructions'])
              color_code = "#DC143C"
              st.markdown(
                  f"""
                  <hr style="border:2px solid {color_code}">
                  """,
                  unsafe_allow_html=True
              )
          elif(shortName[b]['travel_mode']=="TRANSIT"):
              shortTrans = shortName[b]['transit_details']
              if(shortTrans['line']['vehicle']['type']=="SUBWAY"):
                  head = shortTrans['headsign']
                  lineN = head[0]
                  st.write('Take Line', lineN, 'from', \
                                  shortTrans['departure_stop']['name'], 'Station to', \
                                      shortTrans['arrival_stop']['name'], 'Station')
                  color_code = shortTrans['line']['color']
                  st.markdown(
                      f"""
                      <hr style="border:2px solid {color_code}">
                      """,
                      unsafe_allow_html=True
                  )
              elif(shortTrans['line']['vehicle']['type']=="BUS"):
                  head = shortTrans['line']['short_name']
                  st.write('Take Bus No', head, 'from', \
                                  shortTrans['departure_stop']['name'], 'Station to', \
                                      shortTrans['arrival_stop']['name'], 'Station')
                  color_code = shortTrans['line']['color']
                  st.markdown(
                      f"""
                      <hr style="border:2px solid {color_code}">
                      """,
                      unsafe_allow_html=True
                  )
      if st.button(f'Show on map {a+1}', key=f'button_{a}'):
        html_with_json = functions.map_call(st.session_state[f'selected_route_{a}'])

if st.sidebar.button('Show all routes', key ='all'):
   html_with_json = functions.map_call2(st.session_state['selected_route_all'])

# HTML을 Streamlit에 임베드
components.html(html_with_json, height=800, width=1000)
