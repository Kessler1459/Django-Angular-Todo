import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LoginComponent } from './components/login/login.component';
import { SignupComponent } from './components/signup/signup.component';
import { AuthGuard } from './services/auth.guard';
import { NoAuthGuard } from './services/no-auth.guard';

const routes: Routes = [
    { path: "", component: DashboardComponent, canActivate: [AuthGuard] },
    { path: "login", component: LoginComponent, canActivate: [NoAuthGuard] },
    { path: "signup", component: SignupComponent, canActivate: [NoAuthGuard] }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
