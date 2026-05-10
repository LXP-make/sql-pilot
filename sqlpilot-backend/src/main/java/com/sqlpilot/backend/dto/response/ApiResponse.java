package com.sqlpilot.backend.dto.response;

public class ApiResponse<T> {
    private Boolean success;
    private T data;
    private String message;

    public ApiResponse() {
    }

    public ApiResponse(Boolean success, T data, String message) {
        this.success = success;
        this.data = data;
        this.message = message;
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, "Success");
    }

    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(false, null, message);
    }

    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}