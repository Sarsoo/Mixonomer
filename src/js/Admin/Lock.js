import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CardActions, CardContent, Typography, Grid } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

import showMessage from "../Toast.js"

const useStyles = makeStyles({
    root: {
      background: '#9e9e9e',
      color: '#212121'
    },
  });

/**
 * Account lock card component
 */
class Lock extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true,
            accounts: []
        }

        this.getUserInfo();

        this.handleLock = this.handleLock.bind(this);
    }

    /**
     * Make user infor request of API
     */
    getUserInfo(){
        axios.get('/api/users')
        .then((response) => {
            this.setState({
                accounts: response.data.accounts,
                isLoading: false
            })
        })
        .catch((error) => {
            showMessage(`Error Getting User Info (${error.response.status})`);
        });
    }

    /**
     * Make lock request of API
     * @param {*} event Event data
     * @param {*} username Subject username
     * @param {*} to_state Target lock state
     */
    handleLock(event, username, to_state){
        axios.post('/api/user', {
            username: username,
            locked: to_state
        }).catch((error) => {
            var lockMessage = to_state ? 'locking' : 'unlocking';
            showMessage(`Error ${lockMessage} ${username} (${error.response.status})`);
        }).finally(() => {
            this.getUserInfo();
        });
    }

    render() {

        const loadingMessage = <p className="center-text text-no-select">loading...</p>; 

        return this.state.isLoading ? loadingMessage :
            <div style={{maxWidth: '1000px', margin: 'auto', marginTop: '20px'}}>
                <Card align="center">
                    <CardContent>

                        {/* TITLE */}
                        <Typography variant="h4" color="textPrimary">Account Locks</Typography>
                        <Grid container spacing={3}>

                            {/* ACCOUNT CARDS */}
                            { this.state.accounts.map((account) => <Row account={account} handler={this.handleLock}
                            key= {account.username}/>) }
                        </Grid>
                    </CardContent>
                </Card>
            </div>

    }
}

/**
 * Grid of account cards with lock buttons
 * @param {*} props 
 * @returns 
 */
function Row(props){
    const classes = useStyles();
    return (
        <Grid item xs={12} sm={3} md={2}>
            <Card variant="outlined" className={classes.root}>
                <CardContent>

                    {/* USERNAME TITLE */}
                    <Typography variant="h5" color="textSecondary" className={classes.root}>{ props.account.username }</Typography>
                    
                    {/* LAST LOGIN */}
                    <Typography variant="body2" color="textSecondary" className={classes.root}>{ props.account.last_login }</Typography>
                </CardContent>
                <CardActions>

                    {/* LOCK BUTTON */}
                    <Button className="full-width" color="secondary" variant="contained" aria-label="delete" onClick={(e) => props.handler(e, props.account.username, !props.account.locked)}>
                        {props.account.locked ? "Unlock" : "Lock"}
                    </Button>
                </CardActions>
            </Card>
        </Grid>
    );
}

export default Lock;