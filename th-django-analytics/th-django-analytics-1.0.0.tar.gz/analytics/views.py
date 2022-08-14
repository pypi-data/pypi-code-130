from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from analytics.models import Dashboard


class AnalyticView:
    @login_required(login_url="/admin/login/?next=/admin/")
    def dashboard(request, dashId=None):
        # buscando pelo dashboard passado como parâmetro
        if dashId:
            dash_from_user = Dashboard.objects.filter(
                usersAllowed=request.user, dashboard_id=str(dashId)
            ).first()
        else:
            # caso não exista o dashboard com o id buscado
            # renderizamos o primeiro dashboard disponível do usuário
            dash_from_user = Dashboard.objects.filter(
                usersAllowed=request.user
            ).first()

        #  caso o usuário não tenha permissão para acessar nenhum dashboard
        #  ele é redirecionado para a página admin do django
        if not dash_from_user:
            messages.warning(
                request,
                f"Dashboard {dashId} não encontrado",
            )
            return redirect("/admin/analytics/dashboard/")

        #  criando um contexto para enviar ao frontend
        #  contendo os gráficos e seus dados
        context = dash_from_user.create_context(request=request)

        return render(
            request=request, context=context, template_name="analytics.html"
        )
