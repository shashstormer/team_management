// This is sample code for fetching the assign task endpoint

async function assignTask(taskId, assignerUsername, acceptorUsername) {
    const url = '/assign_task';
    const requestData = {
        task_id: taskId,
        assigner_username: assignerUsername,
        acceptor_username: acceptorUsername
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // required else fastapi will raise error
            },
            body: JSON.stringify(requestData),
            credentials: 'include'  // This ensures cookies (including session cookies) are sent with the request
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error: ${response.status} - ${errorData.detail}`);
        }

        const responseData = await response.json();
        console.log('Task assigned successfully:', responseData);
    } catch (error) {
        console.error('Error assigning task:', error);
    }
}

// Usage
assignTask(123, 'assignerUser', 'acceptorUser');
