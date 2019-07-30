import React, { Component } from "react";
const axios = require('axios');

class ChangePassword extends Component {
    
    constructor(props){
        super(props);
        this.state = {
            current: "",
            new1: "",
            new2: "",
            error: false,
            errorValue: null
        }
        this.handleCurrentChange = this.handleCurrentChange.bind(this);
        this.handleNewChange = this.handleNewChange.bind(this);
        this.handleNew2Change = this.handleNew2Change.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleCurrentChange(event){
        this.setState({
            'current': event.target.value
        });
    }
    handleNewChange(event){
        this.setState({
            'new1': event.target.value
        });
    }
    handleNew2Change(event){
        this.setState({
            'new2': event.target.value
        });
    }

    handleSubmit(event){

        if(this.state.current.length == 0){
            this.setState({
                error: true,
                errorValue: "enter current password"
            });
        }else{
            if(this.state.new1.length == 0){
                this.setState({
                    error: true,
                    errorValue: "enter new password"
                });
            }else{
                if(this.state.new1 != this.state.new2){
                this.setState({
                    error: true,
                    errorValue: "new password mismatch"
                });
                }else{

                    axios.post('/api/user/password',{
                        current_password: this.state.current,
                        new_password: this.state.new1
                    }).then((response) => {
                    this.setState({
                        error: true,
                        errorValue: "password changed"
                    });
                    }).catch((error) => {
                        this.setState({
                            error: true,
                            errorValue: "error changing password"
                        });
                    });
                }
            }            
        }

        event.preventDefault();

    }

    render(){
        return (
            <div>
                <h1>change password</h1>
                <form onSubmit={this.handleSubmit}>
                    <table className="app-table max-width">
                        <tbody>
                            <tr>
                                <td className="ui-text center-text">current:</td>
                                <td><input 
                                        type="password" 
                                        name="current" 
                                        value={this.state.current} 
                                        onChange={this.handleCurrentChange}
                                        className="full-width" /></td>
                            </tr>
                            <tr>
                                <td className="ui-text center-text">new:</td>
                                <td><input 
                                        type="password" 
                                        name="new1" 
                                        value={this.state.new1} 
                                        onChange={this.handleNewChange}
                                        className="full-width" /></td>
                            </tr>
                            <tr>
                                <td className="ui-text center-text">new again:</td>
                                <td><input 
                                        type="password" 
                                        name="new2" 
                                        value={this.state.new2} 
                                        onChange={this.handleNew2Change}
                                        className="full-width" /></td>
                            </tr>
                            <tr>
                                <td colSpan="2"><input type="submit" style={{width: "100%"}} className="button" value="change" /></td>
                            </tr>
                        </tbody>
                    </table>
                </form>
                { this.state.error && <p style={{color: "red"}}>{this.state.errorValue}</p>}
            </div>
        );
    }
}

export default ChangePassword;