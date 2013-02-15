BITS 32
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
%define SYS_MMAP 	  192
%define SYS_MUNMAP	  91
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
%define PG_MASK		0xfffff000
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
%define	SIZE_OFF	6
%define STACK_OFF	6 	; for entryp
%define DATA_OFF	10

%define HDR_SIZE	10


	global loader
	global pre_loader
	section .text


pre_loader:
	jmp _data

loader:
	pop ebp			; ebp holds pointer to begin of my list

_load_next:
	xor eax,eax
	mov ax, word [ebp+TYPE_OFF]	; type -- only matter at begining
	cmp eax, LOAD_TYPE
	je _set_load
	cmp eax, STACK_TYPE
	je _set_stack
	cmp eax, ENTRY_TYPE
	je _entryp
	;; die
	jmp _exit


_set_load:

	;; munmap region i dont care if its mmaped or not
	mov ebx, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF]
	mem_align(ecx)
	pusha
	mov eax,SYS_MUNMAP
	int 80h

	;; mmap region again -- always RWX?
	popa 			; vaddr and size are set
	push ebp		; mmap is scary i'd like to save my ptr on header
	mov edx, PROT_READ | PROT_WRITE | PROT_EXEC
	mov esi, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED
	mov edi, 0
	mov ebp, 0
	mov eax, SYS_MMAP
	int 80h

	;; copy stuff
	pop ebp
	lea esi, [ebp + DATA_OFF]
	mov edi, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF ]
	repz movsb
	jmp _next_chunk



_set_stack:			; just copy data, i dont give a shit

	lea esi, [ebp + DATA_OFF]
	mov edi, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF ]
	repz movsb
	jmp _next_chunk

_next_chunk:
	lea eax, [ebp + HDR_SIZE]
	mov ebx, [ebp + SIZE_OFF]
	lea ebp, [eax + ebx]
	jmp _load_next


_entryp:
	mov eax,[ebp + VADDR_OFF]
	mov esp,[ebp + STACK_OFF]
	xor ebx,ebx
	xor ecx,ecx
	xor edx,edx
	xor esi,esi
	xor edi,edi
	jmp eax

_exit:
	mov ebx,1
	mov eax,SYS_EXIT
	int 80h


;;; data is after this
_data:
	call loader
