import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BoardComponent } from './components/board/board.component';
import { SettingsComponent } from './components/board/settings/settings.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LoginComponent } from './components/login/login.component';
import { SignupComponent } from './components/signup/signup.component';
import { AuthGuard } from './services/auth.guard';
import { NoAuthGuard } from './services/no-auth.guard';

const routes: Routes = [
    { path: "", redirectTo: "boards", pathMatch: "full" },
    { path: "boards", component: DashboardComponent, canActivate: [AuthGuard] },
    { path: "boards/:boardId", component: BoardComponent , canActivate: [AuthGuard]},
    { path: "boards/:boardId/settings", component: SettingsComponent , canActivate: [AuthGuard]},
    { path: "login", component: LoginComponent, canActivate: [NoAuthGuard] },
    { path: "signup", component: SignupComponent, canActivate: [NoAuthGuard] }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
