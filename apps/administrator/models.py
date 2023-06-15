#
# from django.contrib.auth.models import Group, Permission
# from django.contrib.auth import get_user_model
#
#
# User = get_user_model()
#
# # Define custom permissions
# can_call_out_of_turn = Permission.objects.get(codename='can_call_out_of_turn')
# can_modify_queue_list = Permission.objects.get(codename='can_modify_queue_list')
# can_create_tickets = Permission.objects.get(codename='can_create_tickets')
# can_close_tickets = Permission.objects.get(codename='can_close_tickets')
#
# # Create a user group
# operator_group, created = Group.objects.get_or_create(name='Operator Group')
#
# # Assign permissions to the user group
# operator_group, created = Group.objects.get_or_create(name='Operator Group')
# operator_group.permissions.add(can_call_out_of_turn, can_create_tickets, can_close_tickets)
#
#
# # Assign permissions to the individual user
# admin_user = User.objects.get(username='admin')
# admin_user.user_permissions.add(can_call_out_of_turn, can_modify_queue_list, can_create_tickets, can_close_tickets)
#
# admin_user.user


