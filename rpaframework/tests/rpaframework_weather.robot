*** Settings ***
Library		flowable.rpaframework_client.API

*** Tasks ***
Get weather forecast
    ${city}=		flw input	city
    ${days}=		flw input	days
    ${length}=      Get Length  ${city}
    ${temperature}=     Evaluate    ${days} * ${length}
    flw output		temperature     ${temperature}