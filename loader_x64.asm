BITS 64
;;;
;;; whole payload:
;;;  - get listptr
;;;  - loader code
;;;  - chunks list
;;;
;;; chunk:
;;; 1) type: LOAD == 1 , STACK == 2 , ENTRYPOINT -- always last
;;; 2) vaddr
;;; 3) size -- page aligned?
;;; 4) data if type != ENTRYPOINT
;;;

;;;  syscalls numbers
%define SYS_MMAP 	  9
%define SYS_MUNMAP	  11
%define SYS_EXIT	  1

;;; mmap stuff - olac

%define PROT_READ	0x1
%define PROT_WRITE	0x2
%define PROT_EXEC	0x4

%define MAP_PRIVATE	0x02
%define MAP_FIXED	0x10
%define MAP_ANONYMOUS	0x20


;;;  paging stuff
%define PG_SIZE		0x1000
%define PG_MASK		~(PG_SIZE-1)
%macro mem_align 1

	add %1, PG_SIZE
	and %1, PG_MASK

%endmacro
;;;  my header stuff
%define LOAD_TYPE	1
%define	STACK_TYPE	2
%define	ENTRY_TYPE	3

%define TYPE_OFF 	0
%define VADDR_OFF 	2
%define	SIZE_OFF	10
%define STACK_OFF	10 	; for entryp
%define DATA_OFF	18

%define HDR_SIZE	18


pre_loader:
	jmp _data

loader:
	pop rbp			; ebp holds pointer to begin of my list

_load_next:
	xor rax,rax
	mov ax, word [ebp+TYPE_OFF]	; type -- only matter at begining
	cmp ax, LOAD_TYPE
	je _set_load
	cmp ax, STACK_TYPE
	je _set_stack
	cmp ax, ENTRY_TYPE
	je _entryp
	;; die
	jmp _exit


_set_load:

	;; munmap region i dont care if its mmaped or not
	mov rdi, [rbp + VADDR_OFF]
	mov rsi, [rbp + SIZE_OFF]
	mem_align(rsi)

	mov rax,SYS_MUNMAP
	syscall

	;; mmap region again -- always RWX?

	mov rdi, [rbp + VADDR_OFF]
	mov rsi, [rbp + SIZE_OFF]
	mem_align(rsi)

	mov rdx, PROT_READ | PROT_WRITE | PROT_EXEC
	mov rcx, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED
	xor r9,r9
	xor r8,r8
	mov r10,rcx
	mov rax, SYS_MMAP
	syscall

	;; copy stuff
	lea rsi, [rbp + DATA_OFF]
	mov rdi, [rbp + VADDR_OFF]
	mov rcx, [rbp + SIZE_OFF ]
	repz movsb
	jmp _next_chunk



_set_stack:			; just copy data, i dont give a shit

	lea rsi, [rbp + DATA_OFF]
	mov rdi, [rbp + VADDR_OFF]
	mov rcx, [rbp + SIZE_OFF ]
	repz movsb
	jmp _next_chunk

_next_chunk:
	lea rax, [rbp + HDR_SIZE]
	mov rbx, [rbp + SIZE_OFF]
	lea rbp, [rax + rbx]
	jmp _load_next


_entryp:
	mov rax,[rbp + VADDR_OFF]
	mov rsp,[rbp + STACK_OFF]
	xor rbx,rbx
	xor rcx,rcx
	xor rdx,rdx
	xor rsi,rsi
	xor rdi,rdi
	jmp rax

_exit:
	mov rdi,1
	mov rax,SYS_EXIT
	syscall


;;; data is after this
_data:
	call loader
