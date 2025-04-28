/**
 * Utility functions for debugging
 */

/**
 * Safely inspect an object for debugging purposes
 * @param obj The object to inspect
 * @returns A string representation of the object
 */
export function inspectObject(obj: unknown): string {
    try {
        if (obj === null) return 'null';
        if (obj === undefined) return 'undefined';

        if (typeof obj === 'object') {
            // Try to get all properties including non-enumerable ones
            const allProps = Object.getOwnPropertyNames(obj);
            const result: Record<string, unknown> = {};

            for (const prop of allProps) {
                try {
                    // @ts-expect-error: We're deliberately accessing props dynamically
                    result[prop] = obj[prop];
                } catch (e) {
                    result[prop] = `[Error getting property: ${e}]`;
                }
            }

            return JSON.stringify(result, null, 2);
        }

        return String(obj);
    } catch (error) {
        return `[Error inspecting object: ${error}]`;
    }
}

/**
 * Log API response details for debugging
 * @param label Description of what's being logged
 * @param response The API response object
 */
export function logApiResponse(label: string, response: any): void {
    console.group(`API Response: ${label}`);

    try {
        console.log('Status:', response.status);
        console.log('Status Text:', response.statusText);
        console.log('Headers:', response.headers);

        console.group('Data');
        if (response.data === undefined) {
            console.log('No data in response');
        } else {
            console.log('Type:', typeof response.data);

            if (typeof response.data === 'object' && response.data !== null) {
                console.log('Keys:', Object.keys(response.data));
                console.log('Full data:', response.data);
            } else {
                console.log('Value:', response.data);
            }
        }
        console.groupEnd();
    } catch (error) {
        console.error('Error logging response:', error);
    }

    console.groupEnd();
}
