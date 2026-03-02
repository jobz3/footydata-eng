{% macro get_result_type(goal_for, goal_against) %}
case
    when {{ goal_for }} > {{ goal_against }} then 'W'
    when {{ goal_for }} = {{ goal_against }} then 'D'
    else 'L'
end
{% endmacro %}
